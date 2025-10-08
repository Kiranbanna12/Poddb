"""YouTube Sync Service for synchronizing podcast data from YouTube"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import time
from database.db import get_db_connection
from services.youtube_service import youtube_service
from services.cloudinary_service import cloudinary_service

logger = logging.getLogger(__name__)


class YouTubeSyncService:
    def __init__(self):
        self.api_calls_made = 0
        self.api_quota_used = 0
    
    def reset_api_counter(self):
        """Reset API call counter"""
        self.api_calls_made = 0
        self.api_quota_used = 0
    
    def track_api_usage(self, quota_cost: int = 1, success: bool = True):
        """
        Track YouTube API usage
        
        Args:
            quota_cost: Quota units consumed by this call
            success: Whether the API call succeeded
        """
        self.api_calls_made += 1
        self.api_quota_used += quota_cost
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get today's midnight timestamp
            today_midnight = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            
            # Check if today's record exists
            cursor.execute("SELECT id, quota_used, requests_count, successful_requests, failed_requests FROM youtube_api_usage WHERE usage_date = ?", (today_midnight,))
            existing = cursor.fetchone()
            
            if existing:
                record_id, current_quota, current_requests, current_success, current_failed = existing
                cursor.execute("""
                    UPDATE youtube_api_usage 
                    SET quota_used = ?, requests_count = ?, 
                        successful_requests = ?, failed_requests = ?
                    WHERE id = ?
                """, (
                    current_quota + quota_cost,
                    current_requests + 1,
                    current_success + (1 if success else 0),
                    current_failed + (0 if success else 1),
                    record_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO youtube_api_usage 
                    (usage_date, quota_used, requests_count, successful_requests, failed_requests)
                    VALUES (?, ?, ?, ?, ?)
                """, (today_midnight, quota_cost, 1, 1 if success else 0, 0 if success else 1))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to track API usage: {e}")
    
    def check_api_quota(self) -> dict:
        """
        Check current API quota usage
        
        Returns:
            dict with quota info
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            today_midnight = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            
            cursor.execute("SELECT quota_used, quota_limit FROM youtube_api_usage WHERE usage_date = ?", (today_midnight,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                quota_used, quota_limit = result
                percentage = (quota_used / quota_limit) * 100
                return {
                    "quota_used": quota_used,
                    "quota_limit": quota_limit,
                    "percentage": percentage,
                    "can_continue": percentage < 90
                }
            else:
                return {
                    "quota_used": 0,
                    "quota_limit": 10000,
                    "percentage": 0,
                    "can_continue": True
                }
        except Exception as e:
            logger.error(f"Failed to check API quota: {e}")
            return {"quota_used": 0, "quota_limit": 10000, "percentage": 0, "can_continue": True}
    
    def sync_podcast_from_youtube(self, podcast_id: int, sync_job_id: int) -> dict:
        """
        Sync a single podcast from YouTube
        
        Args:
            podcast_id: ID of podcast to sync
            sync_job_id: ID of the parent sync job
        
        Returns:
            dict with sync results
        """
        result = {
            "success": False,
            "episodes_updated": 0,
            "new_episodes_added": 0,
            "errors": []
        }
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get podcast data
            cursor.execute("SELECT id, title, youtube_playlist_id FROM podcasts WHERE id = ? AND status = 'approved'", (podcast_id,))
            podcast = cursor.fetchone()
            
            if not podcast:
                result["errors"].append("Podcast not found or not approved")
                return result
            
            pod_id, pod_title, playlist_id = podcast
            
            if not playlist_id:
                result["errors"].append("No YouTube playlist ID")
                return result
            
            logger.info(f"Syncing podcast: {pod_title} (ID: {pod_id})")
            
            # Check API quota
            quota_check = self.check_api_quota()
            if not quota_check["can_continue"]:
                result["errors"].append("API quota limit reached")
                self._log_sync_error(sync_job_id, 'podcast', pod_id, 'rate_limit', 
                                    "YouTube API quota limit reached", playlist_id)
                return result
            
            # Fetch playlist videos from YouTube
            try:
                # playlists.list costs 1 quota unit
                self.track_api_usage(1, True)
                playlist_details = youtube_service.get_playlist_details(playlist_id)
                
                # playlistItems.list costs 1 unit per page (50 videos per page)
                # videos.list costs 1 unit per 50 videos
                # Estimate: 2-3 units per 50 videos
                videos = youtube_service.get_playlist_videos(playlist_id, max_results=None)
                estimated_quota = (len(videos) // 50 + 1) * 3
                self.track_api_usage(estimated_quota, True)
                
                logger.info(f"Fetched {len(videos)} videos from YouTube playlist")
            except Exception as e:
                logger.error(f"Failed to fetch playlist from YouTube: {e}")
                result["errors"].append(f"YouTube API error: {str(e)}")
                self.track_api_usage(1, False)
                self._log_sync_error(sync_job_id, 'podcast', pod_id, 'api_error', str(e), playlist_id)
                conn.close()
                return result
            
            # Get existing episodes
            cursor.execute("SELECT youtube_video_id FROM episodes WHERE podcast_id = ?", (pod_id,))
            existing_video_ids = {row[0] for row in cursor.fetchall() if row[0]}
            
            # Find new episodes
            youtube_video_ids = {video['video_id'] for video in videos}
            new_video_ids = youtube_video_ids - existing_video_ids
            
            logger.info(f"Found {len(new_video_ids)} new episodes to add")
            
            # Add new episodes
            for video in videos:
                if video['video_id'] in new_video_ids:
                    try:
                        # Upload thumbnail to Cloudinary
                        try:
                            thumbnail_result = cloudinary_service.download_and_upload_youtube_thumbnail(
                                video['thumbnail'],
                                video['video_id'],
                                folder="episodes"
                            )
                            thumbnail_url = thumbnail_result['secure_url']
                        except Exception as e:
                            logger.warning(f"Failed to upload thumbnail: {e}")
                            thumbnail_url = video['thumbnail']
                        
                        # Get next episode number
                        cursor.execute("SELECT MAX(episode_number) FROM episodes WHERE podcast_id = ?", (pod_id,))
                        max_ep_num = cursor.fetchone()[0] or 0
                        
                        # Insert new episode
                        cursor.execute("""
                            INSERT INTO episodes 
                            (podcast_id, title, description, youtube_video_id, thumbnail, 
                             episode_number, views, likes, comments, duration, published_date, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pod_id, video['title'], video['description'], video['video_id'],
                            thumbnail_url, max_ep_num + 1, video['views'], video['likes'],
                            video['comments'], video['duration'], video['published_date'],
                            int(time.time())
                        ))
                        
                        result["new_episodes_added"] += 1
                        logger.info(f"Added new episode: {video['title']}")
                    except Exception as e:
                        logger.error(f"Failed to add episode {video['video_id']}: {e}")
                        result["errors"].append(f"Failed to add episode: {video['title']}")
                        self._log_sync_error(sync_job_id, 'episode', None, 'invalid_data', 
                                           str(e), video['video_id'])
            
            # Update existing episodes
            for video in videos:
                if video['video_id'] not in new_video_ids:
                    try:
                        cursor.execute("""
                            UPDATE episodes 
                            SET views = ?, likes = ?, comments = ?
                            WHERE youtube_video_id = ? AND podcast_id = ?
                        """, (video['views'], video['likes'], video['comments'], 
                              video['video_id'], pod_id))
                        
                        if cursor.rowcount > 0:
                            result["episodes_updated"] += 1
                    except Exception as e:
                        logger.error(f"Failed to update episode {video['video_id']}: {e}")
                        result["errors"].append(f"Failed to update episode: {video['title']}")
            
            # Update podcast totals
            cursor.execute("""
                SELECT 
                    COUNT(*) as episode_count,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments
                FROM episodes 
                WHERE podcast_id = ?
            """, (pod_id,))
            
            totals = cursor.fetchone()
            if totals:
                cursor.execute("""
                    UPDATE podcasts 
                    SET episode_count = ?, views = ?, likes = ?, comments = ?, updated_at = ?
                    WHERE id = ?
                """, (totals[0], totals[1] or 0, totals[2] or 0, totals[3] or 0, 
                      int(time.time()), pod_id))
            
            conn.commit()
            conn.close()
            
            result["success"] = True
            logger.info(f"Sync complete for {pod_title}: {result['new_episodes_added']} new, {result['episodes_updated']} updated")
            
        except Exception as e:
            logger.error(f"Error syncing podcast {podcast_id}: {e}")
            result["errors"].append(str(e))
        
        return result
    
    def _log_sync_error(self, sync_job_id: int, entity_type: str, entity_id: Optional[int], 
                       error_type: str, error_message: str, youtube_id: str):
        """Log sync error to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sync_errors 
                (sync_job_id, entity_type, entity_id, error_type, error_message, youtube_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sync_job_id, entity_type, entity_id, error_type, error_message, youtube_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log sync error: {e}")


# Singleton instance
youtube_sync_service = YouTubeSyncService()
