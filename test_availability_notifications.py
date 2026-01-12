#!/usr/bin/env python3
"""
Test script for availability notifications
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from user_account.models import Patient, Practitioner
from practitionerdashboard.models import AvailableSlot
from patientdashboard.models import Appointment
from practitionerdashboard.notifications import send_bulk_availability_notifications
from datetime import datetime, timedelta

def test_availability_notifications():
    """Test the availability notification system"""
    
    print("🏥 Testing Availability Notification System")
    print("=" * 50)
    
    try:
        # Get a test practitioner
        practitioner = Practitioner.objects.first()
        if not practitioner:
            print("❌ No practitioners found in database")
            return
        
        print(f"✅ Using practitioner: Dr. {practitioner.first_name} {practitioner.last_name}")
        
        # Get patients with pending appointments for this practitioner
        pending_appointments = Appointment.objects.filter(
            practitioner=practitioner,
            status='Pending'
        ).select_related('patient')
        
        print(f"✅ Found {pending_appointments.count()} patients with pending appointments")
        
        # Get some available slots for this practitioner
        available_slots = AvailableSlot.objects.filter(
            practitioner=practitioner,
            status='available',
            date__gte=datetime.now().date()
        ).order_by('date', 'start_time')[:3]
        
        print(f"✅ Found {available_slots.count()} available slots")
        
        if available_slots.exists():
            print("\n📅 Available Slots:")
            for slot in available_slots:
                print(f"   - {slot.date} {slot.start_time} - {slot.end_time}")
        
        if pending_appointments.exists():
            print(f"\n👥 Patients to notify:")
            for appointment in pending_appointments:
                print(f"   - {appointment.patient.first_name} {appointment.patient.last_name} ({appointment.patient.email})")
        
        # Test the notification system
        if available_slots.exists() and pending_appointments.exists():
            print(f"\n📧 Sending availability notifications...")
            send_bulk_availability_notifications(practitioner, available_slots)
            print(f"✅ Notifications sent successfully!")
        else:
            print(f"\n⚠️ Cannot test notifications:")
            if not available_slots.exists():
                print(f"   - No available slots found")
            if not pending_appointments.exists():
                print(f"   - No patients with pending appointments found")
        
        print(f"\n📊 System Status:")
        print(f"   - Practitioners: {Practitioner.objects.count()}")
        print(f"   - Patients: {Patient.objects.count()}")
        print(f"   - Total Appointments: {Appointment.objects.count()}")
        print(f"   - Pending Appointments: {Appointment.objects.filter(status='Pending').count()}")
        print(f"   - Available Slots: {AvailableSlot.objects.filter(status='available').count()}")
        
    except Exception as e:
        print(f"❌ Error testing notifications: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_availability_notifications()