"""Analytics Service for calculating daily metrics"""
import logging
from datetime import datetime, timezone
from database.db import get_db_connection

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self):
        pass
    
    def calculate_daily_metrics(self, podcast_id: int = None, episode_id: int = None) -> dict:
        """
        Calculate daily incremental metrics (views_today, likes_today, comments_today)
        by comparing today's totals with yesterday's totals
        
        Args:
            podcast_id: Calculate for specific podcast (None = all podcasts)
            episode_id: Calculate for specific episode (None = all episodes)
        
        Returns:
            dict with stats about calculation
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get today's midnight timestamp
            today_midnight = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            
            # Get yesterday's midnight timestamp
            yesterday_midnight = today_midnight - 86400
            
            episodes_processed = 0
            episodes_updated = 0
            
            # Get episodes to process
            if episode_id:
                cursor.execute("SELECT id, podcast_id, views, likes, comments FROM episodes WHERE id = ?", (episode_id,))
            elif podcast_id:
                cursor.execute("SELECT id, podcast_id, views, likes, comments FROM episodes WHERE podcast_id = ?", (podcast_id,))
            else:
                cursor.execute("SELECT id, podcast_id, views, likes, comments FROM episodes")
            
            episodes = cursor.fetchall()
            
            for episode in episodes:
                ep_id, pod_id, current_views, current_likes, current_comments = episode
                episodes_processed += 1
                
                # Get yesterday's snapshot
                cursor.execute("""
                    SELECT total_views, total_likes, total_comments 
                    FROM daily_analytics 
                    WHERE episode_id = ? AND snapshot_date = ?
                """, (ep_id, yesterday_midnight))
                
                yesterday_data = cursor.fetchone()
                
                if yesterday_data:
                    yesterday_views, yesterday_likes, yesterday_comments = yesterday_data
                    
                    # Calculate incremental metrics
                    views_today = max(0, current_views - yesterday_views)
                    likes_today = max(0, current_likes - yesterday_likes)
                    comments_today = max(0, current_comments - yesterday_comments)
                else:
                    # First sync - don't count historical data as "today"
                    views_today = 0
                    likes_today = 0
                    comments_today = 0
                
                # Check if today's snapshot already exists
                cursor.execute("""
                    SELECT id FROM daily_analytics 
                    WHERE episode_id = ? AND snapshot_date = ?
                """, (ep_id, today_midnight))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing snapshot
                    cursor.execute("""
                        UPDATE daily_analytics 
                        SET total_views = ?, total_likes = ?, total_comments = ?,
                            views_today = ?, likes_today = ?, comments_today = ?
                        WHERE id = ?
                    """, (current_views, current_likes, current_comments,
                          views_today, likes_today, comments_today, existing[0]))
                else:
                    # Insert new snapshot
                    cursor.execute("""
                        INSERT INTO daily_analytics 
                        (podcast_id, episode_id, snapshot_date, total_views, total_likes, total_comments,
                         views_today, likes_today, comments_today)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (pod_id, ep_id, today_midnight, current_views, current_likes, current_comments,
                          views_today, likes_today, comments_today))
                
                episodes_updated += 1
            
            # Calculate podcast-level analytics
            podcasts_updated = 0
            
            if podcast_id:
                podcast_ids = [podcast_id]
            else:
                cursor.execute("SELECT DISTINCT podcast_id FROM episodes")
                podcast_ids = [row[0] for row in cursor.fetchall()]
            
            for pod_id in podcast_ids:
                # Sum episode metrics for this podcast
                cursor.execute("""
                    SELECT 
                        SUM(total_views), SUM(total_likes), SUM(total_comments),
                        SUM(views_today), SUM(likes_today), SUM(comments_today)
                    FROM daily_analytics
                    WHERE podcast_id = ? AND snapshot_date = ?
                """, (pod_id, today_midnight))
                
                podcast_totals = cursor.fetchone()
                
                if podcast_totals and podcast_totals[0] is not None:
                    total_views, total_likes, total_comments, views_today, likes_today, comments_today = podcast_totals
                    
                    # Check if podcast snapshot exists
                    cursor.execute("""
                        SELECT id FROM daily_analytics 
                        WHERE podcast_id = ? AND episode_id IS NULL AND snapshot_date = ?
                    """, (pod_id, today_midnight))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        cursor.execute("""
                            UPDATE daily_analytics 
                            SET total_views = ?, total_likes = ?, total_comments = ?,
                                views_today = ?, likes_today = ?, comments_today = ?
                            WHERE id = ?
                        """, (total_views, total_likes, total_comments,
                              views_today, likes_today, comments_today, existing[0]))
                    else:
                        cursor.execute("""
                            INSERT INTO daily_analytics 
                            (podcast_id, episode_id, snapshot_date, total_views, total_likes, total_comments,
                             views_today, likes_today, comments_today)
                            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?)
                        """, (pod_id, today_midnight, total_views, total_likes, total_comments,
                              views_today, likes_today, comments_today))
                    
                    podcasts_updated += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Daily analytics calculated: {episodes_updated} episodes, {podcasts_updated} podcasts")
            
            return {
                "success": True,
                "episodes_processed": episodes_processed,
                "episodes_updated": episodes_updated,
                "podcasts_updated": podcasts_updated
            }
        
        except Exception as e:
            logger.error(f"Error calculating daily metrics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_analytics(self, days_to_keep: int = 365) -> int:
        """
        Delete analytics data older than specified days
        
        Args:
            days_to_keep: Number of days of data to retain
        
        Returns:
            Number of records deleted
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cutoff_timestamp = int(datetime.now(timezone.utc).timestamp()) - (days_to_keep * 86400)
            
            cursor.execute("DELETE FROM daily_analytics WHERE snapshot_date < ?", (cutoff_timestamp,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old analytics records")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up old analytics: {e}")
            return 0
    
    def get_trending_podcasts(self, days: int = 7, limit: int = 10) -> list:
        """
        Get trending podcasts based on recent daily views
        
        Args:
            days: Number of days to consider
            limit: Maximum number of podcasts to return
        
        Returns:
            List of podcast IDs with their trending scores
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cutoff_timestamp = int(datetime.now(timezone.utc).timestamp()) - (days * 86400)
            
            cursor.execute("""
                SELECT 
                    podcast_id,
                    SUM(views_today) as total_new_views,
                    SUM(likes_today) as total_new_likes
                FROM daily_analytics
                WHERE snapshot_date >= ? AND episode_id IS NOT NULL
                GROUP BY podcast_id
                ORDER BY total_new_views DESC
                LIMIT ?
            """, (cutoff_timestamp, limit))
            
            trending = cursor.fetchall()
            conn.close()
            
            return [{"podcast_id": row[0], "views": row[1], "likes": row[2]} for row in trending]
        
        except Exception as e:
            logger.error(f"Error getting trending podcasts: {e}")
            return []


# Singleton instance
analytics_service = AnalyticsService()