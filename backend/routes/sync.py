"""Sync System API Routes"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
import logging
import time
from datetime import datetime, timezone

from database.db import get_db_connection
from services.sync_service import sync_service
from services.youtube_sync_service import youtube_sync_service
from services.analytics_service import analytics_service
from services.scheduler_service import scheduler_service
from services.email_service import email_service
from models.sync import SyncConfigUpdate, SyncTriggerRequest, EmailTestRequest
from auth.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


async def require_admin(authorization: Optional[str] = Header(None)) -> int:
    """Require admin authentication"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        user_id = get_current_user_id(token)
        
        # Check if user is admin
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != 1:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")


@router.get("/status")
async def get_sync_status(admin_id: int = Depends(require_admin)):
    """Get current sync status"""
    try:
        status = sync_service.get_sync_status()
        
        # Get scheduler info
        scheduler_jobs = scheduler_service.get_jobs()
        
        return {
            "success": True,
            "sync_status": status,
            "scheduler_jobs": scheduler_jobs
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-full-sync")
async def run_full_sync(admin_id: int = Depends(require_admin)):
    """Manually trigger full sync"""
    try:
        result = sync_service.run_full_sync()
        return result
    except Exception as e:
        logger.error(f"Error running full sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-new-episodes")
async def check_new_episodes(admin_id: int = Depends(require_admin)):
    """Check for new episodes only"""
    try:
        result = sync_service.check_new_episodes()
        return result
    except Exception as e:
        logger.error(f"Error checking new episodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-podcast/{podcast_id}")
async def sync_single_podcast(
    podcast_id: int,
    admin_id: int = Depends(require_admin)
):
    """Sync a single podcast manually"""
    try:
        # Create a manual sync job
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sync_jobs (job_type, status) VALUES ('full_sync', 'running')"
        )
        job_id = cursor.lastrowid
        cursor.execute(
            "UPDATE sync_jobs SET started_at = ? WHERE id = ?",
            (int(time.time()), job_id)
        )
        conn.commit()
        conn.close()
        
        # Sync the podcast
        result = youtube_sync_service.sync_podcast_from_youtube(podcast_id, job_id)
        
        # Update job status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sync_jobs 
            SET status = ?, completed_at = ?, duration_seconds = ?,
                items_processed = 1, items_updated = ?, new_episodes_found = ?
            WHERE id = ?
        """, (
            'completed' if result['success'] else 'failed',
            int(time.time()),
            int(time.time()) - int(time.time()),
            1 if result['success'] else 0,
            result['new_episodes_added'],
            job_id
        ))
        conn.commit()
        conn.close()
        
        return {
            "success": result['success'],
            "job_id": job_id,
            "podcast_id": podcast_id,
            "episodes_updated": result['episodes_updated'],
            "new_episodes_added": result['new_episodes_added'],
            "errors": result['errors']
        }
    except Exception as e:
        logger.error(f"Error syncing podcast {podcast_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recalculate-analytics")
async def recalculate_analytics(admin_id: int = Depends(require_admin)):
    """Recalculate daily analytics"""
    try:
        result = analytics_service.calculate_daily_metrics()
        return result
    except Exception as e:
        logger.error(f"Error recalculating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_sync_dashboard(admin_id: int = Depends(require_admin)):
    """Get comprehensive sync dashboard data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current sync status
        sync_status = sync_service.get_sync_status()
        
        # Get last sync job
        cursor.execute("""
            SELECT id, job_type, status, started_at, completed_at, 
                   items_processed, items_updated, new_episodes_found, items_failed
            FROM sync_jobs
            ORDER BY created_at DESC
            LIMIT 1
        """)
        last_sync = cursor.fetchone()
        
        # Get today's stats
        today_midnight = int(datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp())
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT podcast_id) as podcasts_synced,
                COUNT(*) as episodes_synced
            FROM daily_analytics
            WHERE snapshot_date = ?
        """, (today_midnight,))
        today_stats = cursor.fetchone()
        
        # Get error count today
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sync_errors 
            WHERE created_at >= ? AND resolved = 0
        """, (today_midnight,))
        error_count = cursor.fetchone()[0]
        
        # Get API usage today
        cursor.execute("""
            SELECT quota_used, quota_limit, requests_count
            FROM youtube_api_usage
            WHERE usage_date = ?
        """, (today_midnight,))
        api_usage = cursor.fetchone()
        
        # Get next scheduled sync
        scheduler_jobs = scheduler_service.get_jobs()
        next_sync = None
        for job in scheduler_jobs:
            if job['id'] == 'daily_sync':
                next_sync = job['next_run']
                break
        
        conn.close()
        
        return {
            "success": True,
            "current_status": sync_status,
            "last_sync": {
                "id": last_sync[0] if last_sync else None,
                "job_type": last_sync[1] if last_sync else None,
                "status": last_sync[2] if last_sync else None,
                "started_at": last_sync[3] if last_sync else None,
                "completed_at": last_sync[4] if last_sync else None,
                "items_processed": last_sync[5] if last_sync else 0,
                "items_updated": last_sync[6] if last_sync else 0,
                "new_episodes_found": last_sync[7] if last_sync else 0,
                "items_failed": last_sync[8] if last_sync else 0
            },
            "next_sync": next_sync,
            "today_stats": {
                "podcasts_synced": today_stats[0] if today_stats else 0,
                "episodes_synced": today_stats[1] if today_stats else 0,
                "errors": error_count
            },
            "api_usage": {
                "quota_used": api_usage[0] if api_usage else 0,
                "quota_limit": api_usage[1] if api_usage else 10000,
                "requests_count": api_usage[2] if api_usage else 0,
                "percentage": (api_usage[0] / api_usage[1] * 100) if api_usage else 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_sync_jobs(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    admin_id: int = Depends(require_admin)
):
    """Get sync job history with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = """
            SELECT id, job_type, status, started_at, completed_at,
                   duration_seconds, items_processed, items_updated,
                   items_failed, new_episodes_found, error_message, created_at
            FROM sync_jobs
        """
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM sync_jobs"
        if status:
            count_query += " WHERE status = ?"
            cursor.execute(count_query, [status])
        else:
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "jobs": [
                {
                    "id": job[0],
                    "job_type": job[1],
                    "status": job[2],
                    "started_at": job[3],
                    "completed_at": job[4],
                    "duration_seconds": job[5],
                    "items_processed": job[6],
                    "items_updated": job[7],
                    "items_failed": job[8],
                    "new_episodes_found": job[9],
                    "error_message": job[10],
                    "created_at": job[11]
                }
                for job in jobs
            ],
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting sync jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_sync_errors(
    limit: int = 50,
    resolved: Optional[bool] = None,
    admin_id: int = Depends(require_admin)
):
    """Get sync errors"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT e.id, e.sync_job_id, e.entity_type, e.entity_id,
                   e.error_type, e.error_message, e.youtube_id,
                   e.retry_attempt, e.resolved, e.created_at,
                   p.title as podcast_title,
                   ep.title as episode_title
            FROM sync_errors e
            LEFT JOIN podcasts p ON e.entity_type = 'podcast' AND e.entity_id = p.id
            LEFT JOIN episodes ep ON e.entity_type = 'episode' AND e.entity_id = ep.id
        """
        params = []
        
        if resolved is not None:
            query += " WHERE e.resolved = ?"
            params.append(1 if resolved else 0)
        
        query += " ORDER BY e.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        errors = cursor.fetchall()
        
        conn.close()
        
        return {
            "success": True,
            "errors": [
                {
                    "id": err[0],
                    "sync_job_id": err[1],
                    "entity_type": err[2],
                    "entity_id": err[3],
                    "error_type": err[4],
                    "error_message": err[5],
                    "youtube_id": err[6],
                    "retry_attempt": err[7],
                    "resolved": bool(err[8]),
                    "created_at": err[9],
                    "entity_title": err[10] if err[2] == 'podcast' else err[11]
                }
                for err in errors
            ]
        }
    except Exception as e:
        logger.error(f"Error getting sync errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: int,
    admin_id: int = Depends(require_admin)
):
    """Mark error as resolved"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sync_errors SET resolved = 1 WHERE id = ?",
            (error_id,)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Error marked as resolved"}
    except Exception as e:
        logger.error(f"Error resolving error {error_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_sync_config(admin_id: int = Depends(require_admin)):
    """Get sync configuration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT config_key, config_value, config_type, description
            FROM sync_config
        """)
        configs = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "config": {
                row[0]: {
                    "value": row[1],
                    "type": row[2],
                    "description": row[3]
                }
                for row in configs
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_sync_config(
    config_update: SyncConfigUpdate,
    admin_id: int = Depends(require_admin)
):
    """Update sync configuration"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if config key exists
        cursor.execute(
            "SELECT id FROM sync_config WHERE config_key = ?",
            (config_update.config_key,)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Config key not found")
        
        # Update config
        cursor.execute("""
            UPDATE sync_config 
            SET config_value = ?, updated_at = ?
            WHERE config_key = ?
        """, (config_update.config_value, int(time.time()), config_update.config_key))
        
        conn.commit()
        conn.close()
        
        # If sync_schedule_hour changed, update scheduler
        if config_update.config_key == 'sync_schedule_hour':
            try:
                schedule_hour = int(config_update.config_value)
                scheduler_service.update_schedule(schedule_hour)
            except:
                pass
        
        return {
            "success": True,
            "message": f"Config {config_update.config_key} updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-usage")
async def get_api_usage(
    days: int = 30,
    admin_id: int = Depends(require_admin)
):
    """Get YouTube API usage history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get usage for last N days
        cutoff = int(datetime.now(timezone.utc).timestamp()) - (days * 86400)
        
        cursor.execute("""
            SELECT usage_date, quota_used, quota_limit, requests_count,
                   successful_requests, failed_requests
            FROM youtube_api_usage
            WHERE usage_date >= ?
            ORDER BY usage_date DESC
        """, (cutoff,))
        
        usage_data = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "usage": [
                {
                    "date": row[0],
                    "quota_used": row[1],
                    "quota_limit": row[2],
                    "requests_count": row[3],
                    "successful_requests": row[4],
                    "failed_requests": row[5],
                    "percentage": (row[1] / row[2] * 100) if row[2] > 0 else 0
                }
                for row in usage_data
            ]
        }
    except Exception as e:
        logger.error(f"Error getting API usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email(
    email_test: EmailTestRequest,
    admin_id: int = Depends(require_admin)
):
    """Test email configuration"""
    try:
        recipient = email_test.test_email
        if not recipient:
            # Get admin email from config
            recipient = sync_service.get_config_value('admin_email', '')
        
        if not recipient:
            raise HTTPException(
                status_code=400,
                detail="No recipient email provided and no admin email in config"
            )
        
        # Send test email
        result = email_service.send_test_email(recipient)
        
        return {
            "success": result,
            "message": "Test email sent successfully" if result else "Failed to send test email",
            "recipient": recipient
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable")
async def enable_sync(admin_id: int = Depends(require_admin)):
    """Enable sync system"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sync_config 
            SET config_value = 'true', updated_at = ?
            WHERE config_key = 'sync_enabled'
        """, (int(time.time()),))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Sync system enabled"}
    except Exception as e:
        logger.error(f"Error enabling sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable")
async def disable_sync(admin_id: int = Depends(require_admin)):
    """Disable sync system"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sync_config 
            SET config_value = 'false', updated_at = ?
            WHERE config_key = 'sync_enabled'
        """, (int(time.time()),))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Sync system disabled"}
    except Exception as e:
        logger.error(f"Error disabling sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))
