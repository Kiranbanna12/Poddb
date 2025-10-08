"""Email Service for sending notifications via SMTP"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from database.db import get_db_connection

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Load SMTP configuration from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT config_key, config_value FROM sync_config WHERE config_key LIKE 'smtp_%' OR config_key IN ('admin_email', 'enable_email_notifications')")
            rows = cursor.fetchall()
            conn.close()
            
            config = {row[0]: row[1] for row in rows}
            return config
        except Exception as e:
            logger.error(f"Failed to load email config: {e}")
            return {}
    
    def reload_config(self):
        """Reload configuration from database"""
        self.config = self._load_config()
    
    def is_enabled(self) -> bool:
        """Check if email notifications are enabled"""
        return self.config.get('enable_email_notifications', 'false').lower() == 'true'
    
    def test_connection(self) -> dict:
        """Test SMTP connection"""
        if not self.is_enabled():
            return {"success": False, "message": "Email notifications are disabled"}
        
        try:
            smtp_host = self.config.get('smtp_host', '')
            smtp_port = int(self.config.get('smtp_port', '587'))
            smtp_username = self.config.get('smtp_username', '')
            smtp_password = self.config.get('smtp_password', '')
            use_tls = self.config.get('smtp_use_tls', 'true').lower() == 'true'
            
            if not smtp_host or not smtp_username or not smtp_password:
                return {"success": False, "message": "SMTP configuration is incomplete"}
            
            # Create SMTP connection
            if use_tls:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            
            server.login(smtp_username, smtp_password)
            server.quit()
            
            return {"success": True, "message": "SMTP connection successful"}
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return {"success": False, "message": str(e)}
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SMTP"""
        if not self.is_enabled():
            logger.info("Email notifications are disabled, skipping email send")
            return False
        
        try:
            smtp_host = self.config.get('smtp_host', '')
            smtp_port = int(self.config.get('smtp_port', '587'))
            smtp_username = self.config.get('smtp_username', '')
            smtp_password = self.config.get('smtp_password', '')
            from_email = self.config.get('smtp_from_email', smtp_username)
            from_name = self.config.get('smtp_from_name', 'PodDB Pro')
            use_tls = self.config.get('smtp_use_tls', 'true').lower() == 'true'
            
            if not smtp_host or not smtp_username or not smtp_password:
                logger.error("SMTP configuration is incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            if use_tls:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_admin_notification(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Send notification to admin email"""
        admin_email = self.config.get('admin_email', '')
        if not admin_email:
            logger.warning("Admin email not configured")
            return False
        
        return self.send_email(admin_email, subject, body, is_html)
    
    def send_new_episodes_notification(self, podcast_title: str, episode_count: int, episode_titles: list) -> bool:
        """Send notification about new episodes"""
        subject = f"🎙️ New Episodes Added: {podcast_title}"
        
        body = f"""
New episodes have been automatically added to PodDB Pro!

Podcast: {podcast_title}
New Episodes: {episode_count}

Episodes Added:
"""
        for i, title in enumerate(episode_titles[:10], 1):  # Show max 10
            body += f"{i}. {title}\n"
        
        if episode_count > 10:
            body += f"\n... and {episode_count - 10} more episodes"
        
        body += "\n\n---\nPodDB Pro - Automated Sync System"
        
        return self.send_admin_notification(subject, body)
    
    def send_sync_error_notification(self, error_count: int, error_details: str) -> bool:
        """Send notification about sync errors"""
        subject = f"⚠️ Sync Errors Detected ({error_count} errors)"
        
        body = f"""
The automated sync system encountered errors:

Total Errors: {error_count}

Error Details:
{error_details}

Please check the admin dashboard for more information:
/admin/sync

---
PodDB Pro - Automated Sync System
"""
        
        return self.send_admin_notification(subject, body)
    
    def send_api_quota_warning(self, quota_used: int, quota_limit: int) -> bool:
        """Send warning about API quota usage"""
        percentage = (quota_used / quota_limit) * 100
        subject = f"⚠️ YouTube API Quota Warning ({percentage:.1f}% used)"
        
        body = f"""
YouTube API quota usage is approaching the daily limit:

Quota Used: {quota_used:,} / {quota_limit:,} ({percentage:.1f}%)

The sync system will automatically pause if quota reaches 90% to prevent service disruption.

---
PodDB Pro - Automated Sync System
"""
        
        return self.send_admin_notification(subject, body)


# Singleton instance
email_service = EmailService()


# Placeholder functions for auth routes compatibility
def send_verification_email(email: str, username: str, verification_token: str) -> bool:
    """Send verification email (placeholder)"""
    logger.info(f"Verification email would be sent to {email} for user {username}")
    return True


def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
    """Send password reset email (placeholder)"""
    logger.info(f"Password reset email would be sent to {email} for user {username}")
    return True


def send_password_changed_email(email: str, username: str) -> bool:
    """Send password changed notification email (placeholder)"""
    logger.info(f"Password changed email would be sent to {email} for user {username}")
    return True


def send_email_change_verification(email: str, username: str, verification_token: str) -> bool:
    """Send email change verification (placeholder)"""
    logger.info(f"Email change verification would be sent to {email} for user {username}")
    return True


def send_account_banned_email(email: str, username: str, reason: str) -> bool:
    """Send account banned notification email (placeholder)"""
    logger.info(f"Account banned email would be sent to {email} for user {username}, reason: {reason}")
    return True