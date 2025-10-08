"""Scheduler Service for running automated sync jobs"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from services.sync_service import sync_service
from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_initialized = False
    
    def initialize(self):
        """Initialize and start scheduler"""
        if self.is_initialized:
            logger.info("Scheduler already initialized")
            return
        
        try:
            # Add default jobs
            self._add_default_jobs()
            
            # Start scheduler
            self.scheduler.start()
            self.is_initialized = True
            
            logger.info("Scheduler initialized and started")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
    
    def _add_default_jobs(self):
        """Add default scheduled jobs"""
        # Get sync schedule hour from config
        schedule_hour = int(sync_service.get_config_value('sync_schedule_hour', '2'))
        
        # Daily full sync at configured hour (default 2 AM)
        self.scheduler.add_job(
            self.run_daily_sync,
            CronTrigger(hour=schedule_hour, minute=0),
            id='daily_sync',
            name='Daily Full Sync',
            replace_existing=True
        )
        logger.info(f"Scheduled daily sync at {schedule_hour}:00 UTC")
        
        # New episodes check every 6 hours
        self.scheduler.add_job(
            self.run_new_episodes_check,
            CronTrigger(hour='*/6'),
            id='new_episodes_check',
            name='New Episodes Check',
            replace_existing=True
        )
        logger.info("Scheduled new episodes check every 6 hours")
        
        # Analytics calculation daily at 3 AM
        self.scheduler.add_job(
            self.run_analytics_calculation,
            CronTrigger(hour=3, minute=0),
            id='analytics_calculation',
            name='Daily Analytics Calculation',
            replace_existing=True
        )
        logger.info("Scheduled analytics calculation at 3:00 AM UTC")
        
        # Cleanup old analytics weekly
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(day_of_week='sun', hour=4, minute=0),
            id='cleanup_old_data',
            name='Weekly Data Cleanup',
            replace_existing=True
        )
        logger.info("Scheduled weekly data cleanup at Sunday 4:00 AM UTC")
    
    def run_daily_sync(self):
        """Job function for daily sync"""
        try:
            logger.info("Starting scheduled daily sync")
            
            # Check if sync is enabled
            if not sync_service.is_sync_enabled():
                logger.info("Sync is disabled, skipping scheduled sync")
                return
            
            # Run full sync
            result = sync_service.run_full_sync()
            
            if result["success"]:
                logger.info(f"Scheduled sync completed: {result['stats']}")
            else:
                logger.error(f"Scheduled sync failed: {result['message']}")
        except Exception as e:
            logger.error(f"Error in scheduled sync: {e}")
    
    def run_new_episodes_check(self):
        """Job function for new episodes check"""
        try:
            logger.info("Starting scheduled new episodes check")
            
            if not sync_service.get_config_value('new_episode_check_enabled', 'true').lower() == 'true':
                logger.info("New episodes check is disabled, skipping")
                return
            
            result = sync_service.check_new_episodes()
            
            if result["success"]:
                logger.info("Scheduled new episodes check completed")
            else:
                logger.error(f"Scheduled new episodes check failed: {result['message']}")
        except Exception as e:
            logger.error(f"Error in scheduled new episodes check: {e}")
    
    def run_analytics_calculation(self):
        """Job function for analytics calculation"""
        try:
            logger.info("Starting scheduled analytics calculation")
            
            result = analytics_service.calculate_daily_metrics()
            
            if result["success"]:
                logger.info(f"Analytics calculation completed: {result}")
            else:
                logger.error(f"Analytics calculation failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error in analytics calculation: {e}")
    
    def cleanup_old_data(self):
        """Job function for data cleanup"""
        try:
            logger.info("Starting scheduled data cleanup")
            
            # Cleanup old analytics (keep 365 days)
            deleted_count = analytics_service.cleanup_old_analytics(365)
            logger.info(f"Cleaned up {deleted_count} old analytics records")
        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")
    
    def update_schedule(self, schedule_hour: int):
        """Update sync schedule"""
        try:
            # Reschedule daily sync
            self.scheduler.reschedule_job(
                'daily_sync',
                trigger=CronTrigger(hour=schedule_hour, minute=0)
            )
            logger.info(f"Updated daily sync schedule to {schedule_hour}:00 UTC")
            return True
        except Exception as e:
            logger.error(f"Failed to update schedule: {e}")
            return False
    
    def pause_scheduler(self):
        """Pause scheduler"""
        try:
            self.scheduler.pause()
            logger.info("Scheduler paused")
            return True
        except Exception as e:
            logger.error(f"Failed to pause scheduler: {e}")
            return False
    
    def resume_scheduler(self):
        """Resume scheduler"""
        try:
            self.scheduler.resume()
            logger.info("Scheduler resumed")
            return True
        except Exception as e:
            logger.error(f"Failed to resume scheduler: {e}")
            return False
    
    def shutdown(self):
        """Shutdown scheduler"""
        try:
            self.scheduler.shutdown()
            self.is_initialized = False
            logger.info("Scheduler shutdown")
        except Exception as e:
            logger.error(f"Failed to shutdown scheduler: {e}")
    
    def get_jobs(self) -> list:
        """Get list of scheduled jobs"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": next_run
                })
            return jobs
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []


# Singleton instance
scheduler_service = SchedulerService()
