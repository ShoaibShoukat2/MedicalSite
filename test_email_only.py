#!/usr/bin/env python
"""
Test email configuration only
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_simple():
    """Test simple email sending"""
    print("📧 Testing Email Configuration...")
    
    try:
        print(f"Email Backend: {settings.EMAIL_BACKEND}")
        print(f"Email Host: {settings.EMAIL_HOST}")
        print(f"Email Port: {settings.EMAIL_PORT}")
        print(f"Email User: {settings.EMAIL_HOST_USER}")
        print(f"Email TLS: {settings.EMAIL_USE_TLS}")
        print(f"Email SSL: {settings.EMAIL_USE_SSL}")
        
        print("\n📤 Sending test email...")
        
        result = send_mail(
            subject='Medical Platform - Email Test',
            message='This is a test email to verify email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        if result:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed - no error but result is 0")
            return False
            
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def test_notification_email():
    """Test notification email template"""
    print("\n📧 Testing Notification Email Template...")
    
    try:
        from django.template.loader import render_to_string
        
        # Test context
        context = {
            'patient': {'first_name': 'Test', 'last_name': 'Patient'},
            'practitioner': {'first_name': 'Test', 'last_name': 'Doctor'},
            'appointment_time': '2026-01-10 10:00 AM'
        }
        
        # Test template rendering
        html_content = render_to_string('emails/appointment_confirmed.html', context)
        print("✅ Email template rendered successfully")
        
        # Test sending with template
        result = send_mail(
            subject='Medical Platform - Appointment Confirmed (Test)',
            message='Your appointment has been confirmed.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            html_message=html_content,
            fail_silently=False,
        )
        
        if result:
            print("✅ Template email sent successfully!")
            return True
        else:
            print("❌ Template email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Template email error: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 Email Configuration Test")
    print("=" * 30)
    
    success_count = 0
    total_tests = 2
    
    # Test simple email
    if test_email_simple():
        success_count += 1
    
    # Test template email
    if test_notification_email():
        success_count += 1
    
    print(f"\n📊 Email Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 Email system is working perfectly!")
        print("✅ Notifications should now be sent successfully")
    else:
        print("⚠️ Email system has issues")
        print("💡 Try these solutions:")
        print("1. Generate new Gmail App Password")
        print("2. Check Gmail security settings")
        print("3. Use alternative email service")

if __name__ == "__main__":
    main()