#!/usr/bin/env python
"""
Test script for the notification system
This script tests all notification functions
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from user_account.models import Patient, Practitioner, Appointment
from practitionerdashboard.models import AvailableSlot
from practitionerdashboard.notifications import (
    notify_appointment_booked,
    notify_appointment_accepted,
    notify_appointment_cancelled,
    notify_appointment_modified,
    notify_appointment_reminder,
    send_bulk_availability_notifications
)

def test_email_configuration():
    """Test email configuration"""
    print("📧 Testing Email Configuration...")
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        print(f"✅ Email Backend: {settings.EMAIL_BACKEND}")
        print(f"✅ Email Host: {settings.EMAIL_HOST}")
        print(f"✅ Email Port: {settings.EMAIL_PORT}")
        print(f"✅ Email User: {settings.EMAIL_HOST_USER}")
        print(f"✅ Email SSL: {settings.EMAIL_USE_SSL}")
        
        # Test sending a simple email
        print("\n📤 Sending test email...")
        send_mail(
            subject='Medical Platform - Test Email',
            message='This is a test email from your medical platform notification system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False

def test_notification_functions():
    """Test all notification functions"""
    print("\n🔔 Testing Notification Functions...")
    
    try:
        # Get test data
        patients = Patient.objects.all()[:1]
        practitioners = Practitioner.objects.all()[:1]
        appointments = Appointment.objects.all()[:1]
        
        if not patients:
            print("❌ No patients found. Please create a test patient.")
            return False
            
        if not practitioners:
            print("❌ No practitioners found. Please create a test practitioner.")
            return False
        
        patient = patients[0]
        practitioner = practitioners[0]
        
        print(f"✅ Using test patient: {patient.first_name} {patient.last_name}")
        print(f"✅ Using test practitioner: Dr. {practitioner.first_name} {practitioner.last_name}")
        
        # Test appointment booking notification
        if appointments:
            appointment = appointments[0]
            print(f"\n📋 Testing appointment booking notification...")
            notify_appointment_booked(appointment)
            print("✅ Appointment booking notification sent")
            
            print(f"\n✅ Testing appointment acceptance notification...")
            notify_appointment_accepted(appointment)
            print("✅ Appointment acceptance notification sent")
            
            print(f"\n📅 Testing appointment reminder notification...")
            notify_appointment_reminder(appointment, hours_before=24)
            print("✅ Appointment reminder notification sent")
            
            print(f"\n❌ Testing appointment cancellation notification...")
            notify_appointment_cancelled(appointment, reason="Test cancellation")
            print("✅ Appointment cancellation notification sent")
        
        # Test availability notifications
        slots = AvailableSlot.objects.filter(practitioner=practitioner, status='available')[:3]
        if slots:
            print(f"\n🎯 Testing availability notification...")
            send_bulk_availability_notifications(practitioner, slots)
            print("✅ Availability notification sent")
        
        return True
        
    except Exception as e:
        print(f"❌ Notification function error: {e}")
        return False

def test_database_models():
    """Test notification database models"""
    print("\n💾 Testing Database Models...")
    
    try:
        from patientdashboard.models import Notification
        from practitionerdashboard.models import PractitionerNotification
        
        # Test patient notifications
        patient_notifications = Notification.objects.all()[:5]
        print(f"✅ Found {Notification.objects.count()} patient notifications")
        
        # Test practitioner notifications
        practitioner_notifications = PractitionerNotification.objects.all()[:5]
        print(f"✅ Found {PractitionerNotification.objects.count()} practitioner notifications")
        
        # Show recent notifications
        if patient_notifications:
            print("\n📱 Recent Patient Notifications:")
            for notif in patient_notifications:
                print(f"  - {notif.title} ({notif.created_at.strftime('%Y-%m-%d %H:%M')})")
        
        if practitioner_notifications:
            print("\n👨‍⚕️ Recent Practitioner Notifications:")
            for notif in practitioner_notifications:
                print(f"  - {notif.title} ({notif.created_at.strftime('%Y-%m-%d %H:%M')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def show_system_status():
    """Show overall system status"""
    print("\n📊 System Status Summary:")
    print("=" * 40)
    
    try:
        from user_account.models import Patient, Practitioner, Appointment
        from patientdashboard.models import Notification
        from practitionerdashboard.models import PractitionerNotification, AvailableSlot
        
        print(f"👥 Patients: {Patient.objects.count()}")
        print(f"👨‍⚕️ Practitioners: {Practitioner.objects.count()}")
        print(f"📅 Appointments: {Appointment.objects.count()}")
        print(f"🕐 Available Slots: {AvailableSlot.objects.filter(status='available').count()}")
        print(f"📱 Patient Notifications: {Notification.objects.count()}")
        print(f"🔔 Practitioner Notifications: {PractitionerNotification.objects.count()}")
        
        # Show recent activity
        recent_appointments = Appointment.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        print(f"📈 New Appointments (Last 7 days): {recent_appointments}")
        
        unread_patient_notifications = Notification.objects.filter(is_read=False).count()
        unread_practitioner_notifications = PractitionerNotification.objects.filter(is_read=False).count()
        
        print(f"🔴 Unread Patient Notifications: {unread_patient_notifications}")
        print(f"🔴 Unread Practitioner Notifications: {unread_practitioner_notifications}")
        
    except Exception as e:
        print(f"❌ Status error: {e}")

def main():
    """Main test function"""
    print("🏥 Medical Platform - Notification System Test")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test email configuration
    if test_email_configuration():
        success_count += 1
    
    # Test database models
    if test_database_models():
        success_count += 1
    
    # Test notification functions
    if test_notification_functions():
        success_count += 1
    
    # Show system status
    show_system_status()
    success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your notification system is working perfectly.")
        print("\n💡 Next Steps:")
        print("1. Set up cron jobs for automatic reminders")
        print("2. Test with real appointments")
        print("3. Monitor email delivery")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("Make sure your email configuration is correct and database is set up properly.")

if __name__ == "__main__":
    main()