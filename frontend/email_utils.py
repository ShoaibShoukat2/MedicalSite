"""
Email utility functions for reliable OTP delivery across all email providers.
Handles Gmail, Outlook, Yahoo, Orange, custom domains, etc.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
import logging
import time

logger = logging.getLogger(__name__)


def send_otp_email(recipient_email, otp, user_name="", user_type="patient"):
    """
    Send OTP email with enhanced deliverability for all email providers.
    
    Args:
        recipient_email (str): Recipient's email address
        otp (str): 6-digit OTP code
        user_name (str): User's name for personalization
        user_type (str): 'patient' or 'practitioner'
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    
    try:
        # Validate email format
        if not recipient_email or '@' not in recipient_email:
            return False, "Invalid email address format"
        
        # Determine color scheme based on user type
        if user_type == "practitioner":
            primary_color = "#1e40af"
            bg_color = "#dbeafe"
            greeting = f"Hello Dr. {user_name}," if user_name else "Hello,"
        else:
            primary_color = "#0066CC"
            bg_color = "#f0f8ff"
            greeting = f"Hello {user_name}," if user_name else "Hello,"
        
        # Email subject - clear and concise
        subject = "Your Verification Code"
        
        # Plain text version (fallback for text-only email clients)
        text_content = f"""
{greeting}

Your verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
ReeduVie Medical Platform

---
This is an automated message, please do not reply to this email.
        """.strip()
        
        # HTML version (better deliverability and appearance)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Email Verification</title>
    <!--[if mso]>
    <style type="text/css">
        body, table, td {{font-family: Arial, sans-serif !important;}}
    </style>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- Main Container -->
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px 20px 30px; text-align: center;">
                            <h1 style="margin: 0; color: {primary_color}; font-size: 28px; font-weight: bold;">Email Verification</h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 24px; color: #333333;">
                                {greeting}
                            </p>
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 24px; color: #333333;">
                                Your verification code is:
                            </p>
                            
                            <!-- OTP Box -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="background-color: {bg_color}; padding: 25px; text-align: center; border-radius: 8px; border: 2px dashed {primary_color};">
                                        <h2 style="margin: 0; color: {primary_color}; font-size: 42px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                            {otp}
                                        </h2>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Expiry Notice -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 25px;">
                                <tr>
                                    <td style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                                        <p style="margin: 0; font-size: 14px; color: #856404;">
                                            ⏱️ <strong>Important:</strong> This code will expire in 10 minutes.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Security Notice -->
                            <p style="margin: 25px 0 0 0; font-size: 14px; line-height: 20px; color: #666666;">
                                🔒 For your security, never share this code with anyone. If you didn't request this code, please ignore this email.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #f8f9fa; border-top: 1px solid #e9ecef; border-radius: 0 0 10px 10px;">
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666666; text-align: center;">
                                Best regards,<br>
                                <strong>ReeduVie Medical Platform</strong>
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #999999; text-align: center;">
                                This is an automated message, please do not reply to this email.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Email Client Compatibility Note -->
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; width: 100%; margin-top: 20px;">
                    <tr>
                        <td style="text-align: center; padding: 10px;">
                            <p style="margin: 0; font-size: 11px; color: #999999;">
                                © 2024 ReeduVie. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
                
            </td>
        </tr>
    </table>
</body>
</html>
        """.strip()
        
        # Create email message with proper headers for better deliverability
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=f"ReeduVie Medical <{settings.DEFAULT_FROM_EMAIL}>",  # Friendly name
            to=[recipient_email],
            headers={
                'X-Priority': '1',  # High priority
                'X-MSMail-Priority': 'High',  # For Outlook
                'Importance': 'high',  # For other clients
                'X-Mailer': 'ReeduVie Medical Platform',
                'Reply-To': settings.DEFAULT_FROM_EMAIL,
                'List-Unsubscribe': f'<mailto:{settings.DEFAULT_FROM_EMAIL}?subject=unsubscribe>',  # Anti-spam compliance
                'Precedence': 'bulk',  # Helps with spam filters
                'X-Auto-Response-Suppress': 'OOF, DR, RN, NRN, AutoReply',  # Suppress auto-replies
            }
        )
        
        # Attach HTML version
        msg.attach_alternative(html_content, "text/html")
        
        # Set content subtype
        msg.content_subtype = "html"
        
        # Send with retry logic for better reliability
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                msg.send(fail_silently=False)
                logger.info(f"✅ OTP email sent successfully to {recipient_email} (attempt {attempt + 1})")
                return True, None
                
            except Exception as send_error:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Email send attempt {attempt + 1} failed for {recipient_email}: {str(send_error)}. Retrying...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"❌ Failed to send OTP email to {recipient_email} after {max_retries} attempts: {str(send_error)}")
                    return False, f"Failed to send email after {max_retries} attempts: {str(send_error)}"
        
    except Exception as e:
        logger.error(f"❌ Unexpected error sending OTP email to {recipient_email}: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def validate_email_deliverability(email):
    """
    Basic email validation to check if email is likely deliverable.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    import re
    
    # Basic format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    
    # Check for common typos in popular domains
    common_domains = {
        'gmail.com': ['gmial.com', 'gmai.com', 'gmail.co'],
        'outlook.com': ['outlok.com', 'outlook.co'],
        'yahoo.com': ['yaho.com', 'yahoo.co'],
        'hotmail.com': ['hotmial.com', 'hotmail.co'],
    }
    
    domain = email.split('@')[1].lower()
    for correct_domain, typos in common_domains.items():
        if domain in typos:
            return False, f"Did you mean @{correct_domain}?"
    
    # Check for disposable email domains (optional - can be expanded)
    disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
    if domain in disposable_domains:
        return False, "Disposable email addresses are not allowed"
    
    return True, None
