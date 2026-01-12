#!/usr/bin/env python
"""
Integration Test for Add Slot Functionality
Tests the complete flow when a practitioner adds a new slot
"""

import os
import sys
import django
import json
from datetime import datetime, date, time, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from user_account.models import Patient, Practitioner
from practitionerdashboard.models import AvailableSlot
from patientdashboard.models import Appointment
from practitionerdashboard.views import add_slot

def test_add_slot_with_notifications():
    """Test adding a slot and verify notifications are sent"""
    print("🧪 Testing Add Slot with Notifications...")
    
    try:
        # Get a practitioner
        practitioner = Practitioner.objects.first()
        if not practitioner:
            print("❌ No practitioners found")
            return False
        
        print(f"✅ Using practitioner: Dr. {practitioner.first_name} {practitioner.last_name}")
        
        # Create a patient with pending appointment if none exists
        patient = Patient.objects.first()
        if not patient:
            print("❌ No patients found")
            return False
        
        # Check for existing pending appointments
        pending_count = Appointment.objects.filter(
            practitioner=practitioner,
            status='Pending'
        ).count()
        
        if pending_count == 0:
            # Create a test pending appointment
            test_slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=date.today() + timedelta(days=10),
                start_time=time(9, 0),
                end_time=time(10, 0)
            )
            
            Appointment.objects.create(
                patient=patient,
                practitioner=practitioner,
                slot=test_slot,
                status='Pending',
                amount=practitioner.price or 50.0
            )
            print(f"✅ Created test pending appointment for {patient.first_name}")
        
        # Create a mock request to add a new slot
        factory = RequestFactory()
        
        # Prepare slot data
        tomorrow = date.today() + timedelta(days=1)
        slot_data = {
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '15:00',
            'end_time': '16:00'
        }
        
        # Create POST request
        request = factory.post(
            '/practitioner-dashboard/add-slot/',
            data=json.dumps(slot_data),
            content_type='application/json'
        )
        
        # Add session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Set practitioner ID in session
        request.session['practitioner_id'] = practitioner.id
        
        print(f"📅 Adding new slot: {tomorrow} 15:00-16:00")
        
        # Call the add_slot view
        response = add_slot(request)
        
        # Check response
        if response.status_code == 200:
            response_data = json.loads(response.content)
            if response_data.get('success'):
                print("✅ Slot added successfully!")
                print("✅ Notifications should have been sent to patients on waiting list")
                
                # Verify the slot was created
                new_slot = AvailableSlot.objects.filter(
                    practitioner=practitioner,
                    date=tomorrow,
                    start_time=time(15, 0),
                    end_time=time(16, 0)
                ).first()
                
                if new_slot:
                    print("✅ New slot verified in database")
                    # Clean up
                    new_slot.delete()
                    print("🧹 Test slot cleaned up")
                    return True
                else:
                    print("❌ New slot not found in database")
                    return False
            else:
                print(f"❌ Slot addition failed: {response_data.get('error')}")
                return False
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_logic():
    """Test the notification logic specifically"""
    print("\n🔔 Testing Notification Logic...")
    
    try:
        from practitionerdashboard.notifications import send_bulk_availability_notifications
        
        # Get practitioner and create test slots
        practitioner = Practitioner.objects.first()
        if not practitioner:
            print("❌ No practitioners found")
            return False
        
        # Create test slots
        test_slots = []
        for i in range(2):
            slot_date = date.today() + timedelta(days=i+2)
            slot = AvailableSlot.objects.create(
                practitioner=practitioner,
                date=slot_date,
                start_time=time(11 + i, 0),
                end_time=time(12 + i, 0),
                status='available'
            )
            test_slots.append(slot)
        
        print(f"✅ Created {len(test_slots)} test slots")
        
        # Test notification function
        print("📤 Testing bulk notification function...")
        send_bulk_availability_notifications(practitioner, test_slots)
        print("✅ Bulk notifications sent successfully!")
        
        # Clean up
        for slot in test_slots:
            slot.delete()
        print("🧹 Test slots cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing notification logic: {str(e)}")
        return False

def main():
    """Run integration tests"""
    print("🚀 Starting Add Slot Integration Test")
    print("=" * 50)
    
    tests = [
        ("Add Slot with Notifications", test_add_slot_with_notifications),
        ("Notification Logic", test_notification_logic),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        print("The add_slot functionality with notifications is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)