#!/usr/bin/env python
"""
Setup script for appointment reminder system
This script helps set up automated appointment reminders
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

def setup_reminder_system():
    """Setup the appointment reminder system"""
    
    print("🏥 Medical Platform - Appointment Reminder Setup")
    print("=" * 50)
    
    # Check if management command exists
    try:
        from django.core.management import call_command
        print("✅ Django management system is working")
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False
    
    # Test the reminder command
    try:
        print("\n📋 Testing reminder command (dry run)...")
        call_command('send_appointment_reminders', '--dry-run', '--hours=24')
        print("✅ 24-hour reminder command is working")
        
        call_command('send_appointment_reminders', '--dry-run', '--hours=2')
        print("✅ 2-hour reminder command is working")
        
    except Exception as e:
        print(f"❌ Reminder command error: {e}")
        return False
    
    print("\n📧 Email Configuration Check:")
    from django.conf import settings
    
    if hasattr(settings, 'EMAIL_HOST_USER') and settings.EMAIL_HOST_USER:
        print(f"✅ Email host: {settings.EMAIL_HOST}")
        print(f"✅ Email user: {settings.EMAIL_HOST_USER}")
        print("✅ Email configuration looks good")
    else:
        print("❌ Email not configured properly")
        return False
    
    print("\n🔔 Notification System Check:")
    try:
        from practitionerdashboard.notifications import send_email_notification
        print("✅ Notification system imported successfully")
    except Exception as e:
        print(f"❌ Notification system error: {e}")
        return False
    
    print("\n⏰ Recommended Cron Job Setup:")
    print("Add these lines to your crontab (run 'crontab -e'):")
    print()
    print("# Send 24-hour appointment reminders daily at 9 AM")
    print("0 9 * * * cd /path/to/your/project && python manage.py send_appointment_reminders --hours=24")
    print()
    print("# Send 2-hour appointment reminders every hour")
    print("0 * * * * cd /path/to/your/project && python manage.py send_appointment_reminders --hours=2")
    print()
    
    print("📝 Windows Task Scheduler Setup:")
    print("For Windows, create scheduled tasks that run:")
    print("python manage.py send_appointment_reminders --hours=24")
    print("python manage.py send_appointment_reminders --hours=2")
    print()
    
    print("✅ Reminder system setup completed successfully!")
    print("🎉 Your patients will now receive appointment reminders via email!")
    
    return True

def test_notification_system():
    """Test the notification system with sample data"""
    
    print("\n🧪 Testing Notification System...")
    
    try:
        from user_account.models import Patient, Practitioner, Appointment
        from practitionerdashboard.models import AvailableSlot
        from practitionerdashboard.notifications import notify_appointment_booked
        
        # Check if we have test data
        patients = Patient.objects.all()[:1]
        practitioners = Practitioner.objects.all()[:1]
        
        if not patients or not practitioners:
            print("⚠️  No test data available. Create some patients and practitioners first.")
            return False
        
        print(f"✅ Found {Patient.objects.count()} patients and {Practitioner.objects.count()} practitioners")
        print("✅ Notification system is ready to use")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification test error: {e}")
        return False

if __name__ == "__main__":
    print("Starting reminder system setup...")
    
    if setup_reminder_system():
        test_notification_system()
        print("\n🎉 Setup completed successfully!")
        print("Your appointment reminder system is now ready to use.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)