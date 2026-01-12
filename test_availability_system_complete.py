#!/usr/bin/env python
"""
Complete Availability Notification System Test
Tests the entire flow from adding slots to sending notifications
"""

import os
import sys
import django
from datetime import datetime, date, time, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from user_account.models import Patient, Practitioner
from practitionerdashboard.models import AvailableSlot
from patientdashboard.models import Appointment
from practitionerdashboard.notifications import send_bulk_availability_notifications
from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    """Test basic email configuration"""
    print("🔧 Testing Email Configuration...")
    
    try:
        # Test basic email sending
        send_mail(
            subject='Test Email - Availability System',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # This will fail but test config
            fail_silently=False,
        )
        print("✅ Email configuration appears to be working")
        return True
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")
        return False

def test_notification_system():
    """Test the availability notification system"""
    print("\n📧 Testing Availability Notification System...")
    
    try:
        # Get a practitioner (use first available)
        practitioner = Practitioner.objects.first()
        if not practitioner:
            print("❌ No practitioners found in database")
            return False
        
        print(f"✅ Using practitioner: Dr. {practitioner.first_name} {practitioner.last_name}")
        
        # Get patients with pending appointments for this practitioner
        pending_appointments = Appointment.objects.filter(
            practitioner=practitioner,
            status='Pending'
        ).select_related('patient')
        
        print(f"📋 Found {pending_appointments.count()} patients with pending appointments")
        
        if pending_appointments.count() == 0:
            print("ℹ️  No pending appointments found. Creating test data...")
            
            # Get a patient
            patient = Patient.objects.first()
            if not patient:
                print("❌ No patients found in database")
                return False
            
            # Create a test pending appointment
            test_slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=date.today() + timedelta(days=7),
                start_time=time(10, 0),
                end_time=time(11, 0)
            )
            
            test_appointment = Appointment.objects.create(
                patient=patient,
                practitioner=practitioner,
                slot=test_slot,
                status='Pending',
                amount=practitioner.price or 50.0
            )
            
            print(f"✅ Created test appointment for {patient.first_name} {patient.last_name}")
            pending_appointments = [test_appointment]
        
        # Create some new available slots
        new_slots = []
        for i in range(3):
            slot_date = date.today() + timedelta(days=i+1)
            slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=slot_date,
                start_time=time(14 + i, 0),  # 2 PM, 3 PM, 4 PM
                end_time=time(15 + i, 0),   # 3 PM, 4 PM, 5 PM
                status='available'
            )
            new_slots.append(slot)
            print(f"✅ Created new slot: {slot_date} {slot.start_time}-{slot.end_time}")
        
        # Test the notification function
        print("\n📤 Sending availability notifications...")
        send_bulk_availability_notifications(practitioner, new_slots)
        
        print("✅ Availability notifications sent successfully!")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        for slot in new_slots:
            slot.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing notification system: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_email_template():
    """Test if email template exists and is accessible"""
    print("\n📄 Testing Email Template...")
    
    try:
        from django.template.loader import get_template
        template = get_template('emails/new_availability.html')
        print("✅ Email template found and accessible")
        return True
    except Exception as e:
        print(f"❌ Email template error: {str(e)}")
        return False

def test_models_and_relationships():
    """Test database models and relationships"""
    print("\n🗄️  Testing Database Models...")
    
    try:
        # Test Practitioner model
        practitioner_count = Practitioner.objects.count()
        print(f"✅ Practitioners in database: {practitioner_count}")
        
        # Test Patient model
        patient_count = Patient.objects.count()
        print(f"✅ Patients in database: {patient_count}")
        
        # Test AvailableSlot model
        slot_count = AvailableSlot.objects.count()
        print(f"✅ Available slots in database: {slot_count}")
        
        # Test Appointment model
        appointment_count = Appointment.objects.count()
        print(f"✅ Appointments in database: {appointment_count}")
        
        # Test pending appointments
        pending_count = Appointment.objects.filter(status='Pending').count()
        print(f"✅ Pending appointments: {pending_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Complete Availability Notification System Test")
    print("=" * 60)
    
    tests = [
        ("Email Configuration", test_email_configuration),
        ("Email Template", test_email_template),
        ("Database Models", test_models_and_relationships),
        ("Notification System", test_notification_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The availability notification system is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)