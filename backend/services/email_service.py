"""
Email service for authentication system
Handles email template generation and queuing
"""
import os
from typing import Optional
from database.auth_queries import queue_email

# Get frontend URL from environment
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

def generate_verification_email_html(username: str, verification_link: str) -> str:
    """Generate HTML for email verification email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #000000;
                color: #ffffff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #1F1F1F;
                border-radius: 8px;
                padding: 40px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo h1 {{
                color: #F5C518;
                font-size: 32px;
                margin: 0;
            }}
            .content {{
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                background-color: #5799EF;
                color: #ffffff;
                padding: 14px 30px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #333;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>PodDB Pro</h1>
            </div>
            <div class="content">
                <h2>Welcome to PodDB Pro!</h2>
                <p>Hi {username},</p>
                <p>Thanks for signing up! Please verify your email address to activate your account.</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #5799EF;">{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 PodDB Pro. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_password_reset_email_html(username: str, reset_link: str) -> str:
    """Generate HTML for password reset email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #000000;
                color: #ffffff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #1F1F1F;
                border-radius: 8px;
                padding: 40px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo h1 {{
                color: #F5C518;
                font-size: 32px;
                margin: 0;
            }}
            .content {{
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                background-color: #5799EF;
                color: #ffffff;
                padding: 14px 30px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .warning {{
                background-color: #D9534F;
                color: #ffffff;
                padding: 12px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #333;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>PodDB Pro</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hi {username},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #5799EF;">{reset_link}</p>
                <p>This link will expire in 1 hour.</p>
                <div class="warning">
                    <strong>Security Notice:</strong> If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2025 PodDB Pro. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_password_changed_email_html(username: str) -> str:
    """Generate HTML for password changed notification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #000000;
                color: #ffffff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #1F1F1F;
                border-radius: 8px;
                padding: 40px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo h1 {{
                color: #F5C518;
                font-size: 32px;
                margin: 0;
            }}
            .content {{
                line-height: 1.6;
            }}
            .success {{
                background-color: #5CB85C;
                color: #ffffff;
                padding: 12px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #333;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>PodDB Pro</h1>
            </div>
            <div class="content">
                <h2>Password Changed Successfully</h2>
                <p>Hi {username},</p>
                <div class="success">
                    Your password has been changed successfully.
                </div>
                <p>If you didn't make this change, please contact our support team immediately.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 PodDB Pro. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_account_banned_email_html(username: str, reason: str) -> str:
    """Generate HTML for account banned notification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #000000;
                color: #ffffff;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #1F1F1F;
                border-radius: 8px;
                padding: 40px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo h1 {{
                color: #F5C518;
                font-size: 32px;
                margin: 0;
            }}
            .content {{
                line-height: 1.6;
            }}
            .danger {{
                background-color: #D9534F;
                color: #ffffff;
                padding: 12px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #333;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>PodDB Pro</h1>
            </div>
            <div class="content">
                <h2>Account Suspended</h2>
                <p>Hi {username},</p>
                <div class="danger">
                    Your account has been suspended.
                </div>
                <p><strong>Reason:</strong> {reason}</p>
                <p>If you believe this is a mistake, please contact our support team.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 PodDB Pro. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_verification_email(email: str, username: str, token: str) -> int:
    """Queue verification email"""
    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"
    subject = "Verify your PodDB Pro account"
    body = generate_verification_email_html(username, verification_link)
    
    return queue_email(email, subject, body)

def send_password_reset_email(email: str, username: str, token: str) -> int:
    """Queue password reset email"""
    reset_link = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    subject = "Reset your PodDB Pro password"
    body = generate_password_reset_email_html(username, reset_link)
    
    return queue_email(email, subject, body)

def send_password_changed_email(email: str, username: str) -> int:
    """Queue password changed notification email"""
    subject = "Your PodDB Pro password was changed"
    body = generate_password_changed_email_html(username)
    
    return queue_email(email, subject, body)

def send_account_banned_email(email: str, username: str, reason: str) -> int:
    """Queue account banned notification email"""
    subject = "Your PodDB Pro account has been suspended"
    body = generate_account_banned_email_html(username, reason)
    
    return queue_email(email, subject, body)

def send_email_change_verification(email: str, username: str, token: str) -> int:
    """Queue email change verification"""
    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"
    subject = "Verify your new email address"
    body = generate_verification_email_html(username, verification_link)
    
    return queue_email(email, subject, body)
