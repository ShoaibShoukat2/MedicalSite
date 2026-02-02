#!/usr/bin/env python
"""
Test script to verify notification system functionality
Run this from Django shell: python manage.py shell < test_notifications.py
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from patientdashboard.models import Appointment
from practitionerdashboard.notifications import notify_appointment_accepted, notify_appointment_cancelled
from user_account.models import Patient, Practitioner

def test_notification_system():
    print("🔍 Testing Notification System...")
    
    # Get a sample appointment
    try:
        appointment = Appointment.objects.filter(status='Accepted').first()
        if not appointment:
            print("❌ No accepted appointments found for testing")
            return
        
        print(f"📋 Testing with appointment ID: {appointment.id}")
        print(f"👤 Patient: {appointment.patient.first_name} {appointment.patient.last_name}")
        print(f"👨‍⚕️ Practitioner: {appointment.practitioner.first_name} {appointment.practitioner.last_name}")
        print(f"📧 Patient email: {appointment.patient.email}")
        print(f"📧 Practitioner email: {appointment.practitioner.email}")
        
        # Test acceptance notification
        print("\n🧪 Testing acceptance notification...")
        try:
            notify_appointment_accepted(appointment)
            print("✅ Acceptance notification sent successfully")
        except Exception as e:
            print(f"❌ Acceptance notification failed: {str(e)}")
        
        # Test cancellation notification
        print("\n🧪 Testing cancellation notification...")
        try:
            notify_appointment_cancelled(appointment, reason="Test cancellation", cancelled_by="practitioner")
            print("✅ Cancellation notification sent successfully")
        except Exception as e:
            print(f"❌ Cancellation notification failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")

def check_email_settings():
    print("\n📧 Checking Email Settings...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

def check_templates():
    print("\n📄 Checking Email Templates...")
    import os
    from django.conf import settings
    
    template_dir = os.path.join(settings.BASE_DIR, 'templates', 'emails')
    french_template_dir = os.path.join(template_dir, 'fr')
    
    print(f"Template directory: {template_dir}")
    print(f"French template directory: {french_template_dir}")
    
    if os.path.exists(template_dir):
        print("✅ Email templates directory exists")
        templates = os.listdir(template_dir)
        print(f"Templates found: {templates}")
    else:
        print("❌ Email templates directory not found")
    
    if os.path.exists(french_template_dir):
        print("✅ French email templates directory exists")
        french_templates = os.listdir(french_template_dir)
        print(f"French templates found: {french_templates}")
    else:
        print("❌ French email templates directory not found")

if __name__ == "__main__":
    check_email_settings()
    check_templates()
    test_notification_system()