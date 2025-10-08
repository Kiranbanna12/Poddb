"""Main Sync Service - Orchestrates all sync operations"""
import logging
import time
from typing import Optional
from datetime import datetime, timezone
from database.db import get_db_connection
from services.youtube_sync_service import youtube_sync_service
from services.analytics_service import analytics_service
from services.email_service import email_service

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self):
        self.current_job_id = None
        self.is_running = False
    
    def get_config_value(self, key: str, default: str = '') -> str:
        """Get configuration value from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT config_value FROM sync_config WHERE config_key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else default
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def is_sync_enabled(self) -> bool:
        """Check if sync is enabled"""
        return self.get_config_value('sync_enabled', 'false').lower() == 'true'
    
    def run_full_sync(self) -> dict:
        """
        Run full sync of all approved podcasts
        
        Returns:
            dict with sync results and job ID
        """
        if self.is_running:
            return {"success": False, "message": "Another sync is already running"}
        
        if not self.is_sync_enabled():
            return {"success": False, "message": "Sync system is disabled"}
        
        self.is_running = True
        
        try:
            # Create sync job
            job_id = self._create_sync_job('full_sync')
            self.current_job_id = job_id
            
            # Update job status to running
            self._update_sync_job(job_id, 'running', started_at=int(time.time()))
            
            logger.info(f"Starting full sync (Job ID: {job_id})")
            
            # Get all approved podcasts with YouTube playlist IDs
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title 
                FROM podcasts 
                WHERE status = 'approved' AND youtube_playlist_id IS NOT NULL AND youtube_playlist_id != ''
            """)
            podcasts = cursor.fetchall()
            conn.close()
            
            total_podcasts = len(podcasts)
            logger.info(f"Found {total_podcasts} podcasts to sync")
            
            # Get batch size from config
            batch_size = int(self.get_config_value('sync_batch_size', '50'))
            
            # Process podcasts in batches
            items_processed = 0
            items_updated = 0
            items_failed = 0
            new_episodes_found = 0
            all_new_episodes = []
            
            for i in range(0, total_podcasts, batch_size):
                batch = podcasts[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(total_podcasts + batch_size - 1)//batch_size}")
                
                for podcast_id, podcast_title in batch:
                    # Check API quota before each podcast
                    quota_check = youtube_sync_service.check_api_quota()
                    if not quota_check["can_continue"]:
                        logger.warning("API quota limit reached, pausing sync")
                        self._update_sync_job(job_id, 'paused', 
                                            items_processed=items_processed,
                                            items_updated=items_updated,
                                            items_failed=items_failed,
                                            new_episodes_found=new_episodes_found,
                                            error_message="API quota limit reached (90%)")
                        
                        # Send quota warning email
                        email_service.send_api_quota_warning(
                            quota_check["quota_used"],
                            quota_check["quota_limit"]
                        )
                        
                        self.is_running = False
                        return {
                            "success": False,
                            "message": "Sync paused due to API quota limit",
                            "job_id": job_id,
                            "stats": {
                                "items_processed": items_processed,
                                "items_updated": items_updated,
                                "items_failed": items_failed,
                                "new_episodes_found": new_episodes_found
                            }
                        }
                    
                    # Sync podcast
                    try:
                        logger.info(f"Syncing podcast: {podcast_title} (ID: {podcast_id})")
                        result = youtube_sync_service.sync_podcast_from_youtube(podcast_id, job_id)
                        
                        items_processed += 1
                        
                        if result["success"]:
                            items_updated += 1
                            new_episodes_found += result["new_episodes_added"]
                            
                            # Track new episodes for notification
                            if result["new_episodes_added"] > 0:
                                all_new_episodes.append({
                                    "podcast_id": podcast_id,
                                    "podcast_title": podcast_title,
                                    "count": result["new_episodes_added"]
                                })
                        else:
                            items_failed += 1
                            logger.error(f"Failed to sync {podcast_title}: {result['errors']}")
                    
                    except Exception as e:
                        items_processed += 1
                        items_failed += 1
                        logger.error(f"Exception syncing {podcast_title}: {e}")
                    
                    # Small delay to avoid overwhelming API
                    time.sleep(0.5)
            
            # Calculate daily analytics
            logger.info("Calculating daily analytics...")
            analytics_result = analytics_service.calculate_daily_metrics()
            
            # Complete job
            completed_at = int(time.time())
            duration = completed_at - self._get_job_start_time(job_id)
            
            self._update_sync_job(
                job_id, 'completed',
                completed_at=completed_at,
                duration_seconds=duration,
                items_processed=items_processed,
                items_updated=items_updated,
                items_failed=items_failed,
                new_episodes_found=new_episodes_found
            )
            
            logger.info(f"Full sync completed (Job ID: {job_id}): {items_updated}/{items_processed} podcasts updated, {new_episodes_found} new episodes")
            
            # Send notifications
            if new_episodes_found > 0:
                self._send_new_episodes_notification(all_new_episodes)
            
            if items_failed > 0:
                self._send_error_notification(job_id, items_failed)
            
            self.is_running = False
            self.current_job_id = None
            
            return {
                "success": True,
                "message": "Sync completed successfully",
                "job_id": job_id,
                "stats": {
                    "items_processed": items_processed,
                    "items_updated": items_updated,
                    "items_failed": items_failed,
                    "new_episodes_found": new_episodes_found,
                    "duration_seconds": duration
                }
            }
        
        except Exception as e:
            logger.error(f"Error in full sync: {e}")
            if self.current_job_id:
                self._update_sync_job(self.current_job_id, 'failed', error_message=str(e))
            
            self.is_running = False
            self.current_job_id = None
            
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "job_id": self.current_job_id
            }
    
    def check_new_episodes(self) -> dict:
        """
        Quick check for new episodes only (no full sync)
        
        Returns:
            dict with check results
        """
        if not self.get_config_value('new_episode_check_enabled', 'true').lower() == 'true':
            return {"success": False, "message": "New episode checking is disabled"}
        
        try:
            job_id = self._create_sync_job('new_episodes_check')
            self._update_sync_job(job_id, 'running', started_at=int(time.time()))
            
            logger.info(f"Starting new episodes check (Job ID: {job_id})")
            
            # Get all approved podcasts with YouTube playlist IDs
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title 
                FROM podcasts 
                WHERE status = 'approved' AND youtube_playlist_id IS NOT NULL AND youtube_playlist_id != ''
            """)
            podcasts = cursor.fetchall()
            conn.close()
            
            total_podcasts = len(podcasts)
            logger.info(f"Checking {total_podcasts} podcasts for new episodes")
            
            # Process podcasts
            items_processed = 0
            items_updated = 0
            items_failed = 0
            new_episodes_found = 0
            all_new_episodes = []
            
            for podcast_id, podcast_title in podcasts:
                # Check API quota before each podcast
                quota_check = youtube_sync_service.check_api_quota()
                if not quota_check["can_continue"]:
                    logger.warning("API quota limit reached, pausing check")
                    self._update_sync_job(job_id, 'paused', 
                                        items_processed=items_processed,
                                        items_updated=items_updated,
                                        items_failed=items_failed,
                                        new_episodes_found=new_episodes_found,
                                        error_message="API quota limit reached (90%)")
                    
                    # Send quota warning email
                    email_service.send_api_quota_warning(
                        quota_check["quota_used"],
                        quota_check["quota_limit"]
                    )
                    
                    return {
                        "success": False,
                        "message": "Check paused due to API quota limit",
                        "job_id": job_id,
                        "stats": {
                            "items_processed": items_processed,
                            "items_updated": items_updated,
                            "items_failed": items_failed,
                            "new_episodes_found": new_episodes_found
                        }
                    }
                
                # Sync podcast (this will fetch all episodes including new ones)
                try:
                    logger.info(f"Checking podcast: {podcast_title} (ID: {podcast_id})")
                    result = youtube_sync_service.sync_podcast_from_youtube(podcast_id, job_id)
                    
                    items_processed += 1
                    
                    if result["success"]:
                        items_updated += 1
                        new_episodes_found += result["new_episodes_added"]
                        
                        # Track new episodes for notification
                        if result["new_episodes_added"] > 0:
                            all_new_episodes.append({
                                "podcast_id": podcast_id,
                                "podcast_title": podcast_title,
                                "count": result["new_episodes_added"]
                            })
                            logger.info(f"Found {result['new_episodes_added']} new episodes for {podcast_title}")
                    else:
                        items_failed += 1
                        logger.error(f"Failed to check {podcast_title}: {result['errors']}")
                
                except Exception as e:
                    items_processed += 1
                    items_failed += 1
                    logger.error(f"Exception checking {podcast_title}: {e}")
                
                # Small delay to avoid overwhelming API
                time.sleep(0.5)
            
            # Complete job
            completed_at = int(time.time())
            duration = completed_at - self._get_job_start_time(job_id)
            
            self._update_sync_job(
                job_id, 'completed',
                completed_at=completed_at,
                duration_seconds=duration,
                items_processed=items_processed,
                items_updated=items_updated,
                items_failed=items_failed,
                new_episodes_found=new_episodes_found
            )
            
            logger.info(f"New episodes check completed (Job ID: {job_id}): {new_episodes_found} new episodes found")
            
            # Send notifications
            if new_episodes_found > 0:
                self._send_new_episodes_notification(all_new_episodes)
            
            return {
                "success": True,
                "message": f"Check completed: {new_episodes_found} new episodes found",
                "job_id": job_id,
                "stats": {
                    "items_processed": items_processed,
                    "items_updated": items_updated,
                    "items_failed": items_failed,
                    "new_episodes_found": new_episodes_found,
                    "duration_seconds": duration
                }
            }
        
        except Exception as e:
            logger.error(f"Error checking new episodes: {e}")
            if job_id:
                self._update_sync_job(job_id, 'failed', error_message=str(e))
            return {"success": False, "message": str(e), "job_id": job_id if 'job_id' in locals() else None}
    
    def get_sync_status(self) -> dict:
        """Get current sync status"""
        if not self.is_running:
            return {"is_running": False, "job_id": None}
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, job_type, status, started_at, items_processed, items_updated, new_episodes_found
                FROM sync_jobs
                WHERE id = ?
            """, (self.current_job_id,))
            job = cursor.fetchone()
            conn.close()
            
            if job:
                return {
                    "is_running": True,
                    "job_id": job[0],
                    "job_type": job[1],
                    "status": job[2],
                    "started_at": job[3],
                    "items_processed": job[4],
                    "items_updated": job[5],
                    "new_episodes_found": job[6]
                }
            else:
                return {"is_running": False, "job_id": None}
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {"is_running": False, "job_id": None}
    
    def _create_sync_job(self, job_type: str) -> int:
        """Create new sync job record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sync_jobs (job_type, status) VALUES (?, 'pending')", (job_type,))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def _update_sync_job(self, job_id: int, status: str, **kwargs):
        """Update sync job record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = ["status = ?"]
        update_values = [status]
        
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)
        
        update_values.append(job_id)
        
        query = f"UPDATE sync_jobs SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        
        conn.commit()
        conn.close()
    
    def _get_job_start_time(self, job_id: int) -> int:
        """Get job start time"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT started_at FROM sync_jobs WHERE id = ?", (job_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else int(time.time())
    
    def _send_new_episodes_notification(self, new_episodes_list: list):
        """Send notification about new episodes"""
        try:
            if not new_episodes_list:
                return
            
            # Group by podcast
            total_episodes = sum(ep["count"] for ep in new_episodes_list)
            
            # Send email for first few podcasts
            for podcast_info in new_episodes_list[:5]:
                # Get episode titles
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT title FROM episodes 
                    WHERE podcast_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (podcast_info["podcast_id"], podcast_info["count"]))
                episode_titles = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                email_service.send_new_episodes_notification(
                    podcast_info["podcast_title"],
                    podcast_info["count"],
                    episode_titles
                )
            
            # Send in-app notification
            self._create_admin_notification(
                "New Episodes Added",
                f"{total_episodes} new episodes added across {len(new_episodes_list)} podcasts",
                "/admin/sync"
            )
        except Exception as e:
            logger.error(f"Failed to send new episodes notification: {e}")
    
    def _send_error_notification(self, job_id: int, error_count: int):
        """Send notification about sync errors"""
        try:
            # Get recent errors
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entity_type, error_type, error_message
                FROM sync_errors
                WHERE sync_job_id = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (job_id,))
            errors = cursor.fetchall()
            conn.close()
            
            error_details = "\n".join([f"- {e[0]} ({e[1]}): {e[2]}" for e in errors])
            
            email_service.send_sync_error_notification(error_count, error_details)
            
            self._create_admin_notification(
                "Sync Errors Detected",
                f"{error_count} errors occurred during sync. Check admin dashboard for details.",
                "/admin/sync"
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def _create_admin_notification(self, title: str, message: str, link: str):
        """Create in-app notification for admins"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get all admin users
            cursor.execute("SELECT id FROM users WHERE is_admin = 1")
            admin_ids = [row[0] for row in cursor.fetchall()]
            
            # Create notification for each admin
            for admin_id in admin_ids:
                cursor.execute("""
                    INSERT INTO notifications (user_id, type, title, message, link)
                    VALUES (?, 'sync', ?, ?, ?)
                """, (admin_id, title, message, link))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to create admin notification: {e}")


# Singleton instance
sync_service = SyncService()
