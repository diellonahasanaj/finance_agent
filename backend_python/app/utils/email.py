"""
Email utility functions for sending verification and password reset emails.
In production, integrate with services like SendGrid, AWS SES, or SMTP.
"""

import logging
from app.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

async def send_verification_email(email: str, token: str) -> bool:
    """
    Send email verification email to user.
    In production, integrate with actual email service.
    """
    try:
        # For development, just log the verification link
        verification_link = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email?token={token}"
        logger.info(f"Email verification link for {email}: {verification_link}")
        
        # TODO: Implement actual email sending
        # Example with SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # 
        # message = Mail(
        #     from_email='noreply@personalfinance.com',
        #     to_emails=email,
        #     subject='Verify Your Email Address',
        #     html_content=f'''
        #     <h2>Welcome to Personal Finance Advisor!</h2>
        #     <p>Please click the link below to verify your email address:</p>
        #     <a href="{verification_link}">Verify Email</a>
        #     <p>This link will expire in 24 hours.</p>
        #     '''
        # )
        # 
        # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        # response = sg.send(message)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False

async def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email to user.
    In production, integrate with actual email service.
    """
    try:
        # For development, just log the reset link
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
        logger.info(f"Password reset link for {email}: {reset_link}")
        
        # TODO: Implement actual email sending
        # Example with SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # 
        # message = Mail(
        #     from_email='noreply@personalfinance.com',
        #     to_emails=email,
        #     subject='Reset Your Password',
        #     html_content=f'''
        #     <h2>Password Reset Request</h2>
        #     <p>You requested to reset your password. Click the link below:</p>
        #     <a href="{reset_link}">Reset Password</a>
        #     <p>This link will expire in 1 hour.</p>
        #     <p>If you didn't request this, please ignore this email.</p>
        #     '''
        # )
        # 
        # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        # response = sg.send(message)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

def get_email_template(template_type: str, data: dict) -> str:
    """
    Get email template by type with dynamic data.
    """
    templates = {
        'verification': f"""
        <h2>Welcome to Personal Finance Advisor!</h2>
        <p>Thank you for registering. Please click the link below to verify your email address:</p>
        <a href="{data.get('verification_link')}" style="
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
        ">Verify Email</a>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't create an account, please ignore this email.</p>
        """,
        
        'password_reset': f"""
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Click the link below to proceed:</p>
        <a href="{data.get('reset_link')}" style="
            background-color: #dc3545;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
        ">Reset Password</a>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """,
        
        'welcome': f"""
        <h2>Welcome to Personal Finance Advisor!</h2>
        <p>Hi {data.get('name', 'User')},</p>
        <p>Your account has been successfully verified and is now active!</p>
        <p>You can now:</p>
        <ul>
            <li>Track your expenses and income</li>
            <li>Set and monitor budgets</li>
            <li>Get personalized financial recommendations</li>
            <li>View detailed financial reports</li>
        </ul>
        <p>Click <a href="{settings.FRONTEND_URL.rstrip("/")}/dashboard">here</a> to get started!</p>
        <p>Best regards,<br>The Personal Finance Advisor Team</p>
        """
    }
    
    return templates.get(template_type, "")
