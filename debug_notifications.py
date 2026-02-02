"""
Debug script for notification system
Run with: python manage.py shell < debug_notifications.py
"""

def debug_notification_system():
    print("🔍 DEBUGGING NOTIFICATION SYSTEM")
    print("=" * 50)
    
    # Check Django settings
    from django.conf import settings
    print("\n📧 EMAIL CONFIGURATION:")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'NOT SET')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
    
    # Check if notification functions exist
    print("\n🔧 NOTIFICATION FUNCTIONS:")
    try:
        from practitionerdashboard.notifications import notify_appointment_accepted, notify_appointment_cancelled
        print("✅ notify_appointment_accepted - FOUND")
        print("✅ notify_appointment_cancelled - FOUND")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Check if models exist
    print("\n📊 DATABASE MODELS:")
    try:
        from patientdashboard.models import Appointment
        from user_account.models import Patient, Practitioner
        print("✅ Appointment model - FOUND")
        print("✅ Patient model - FOUND")
        print("✅ Practitioner model - FOUND")
    except ImportError as e:
        print(f"❌ Model import error: {e}")
        return
    
    # Check for sample data
    print("\n📋 SAMPLE DATA:")
    appointments = Appointment.objects.all()[:3]
    print(f"Total appointments: {Appointment.objects.count()}")
    
    for apt in appointments:
        print(f"  Appointment {apt.id}: {apt.patient.first_name} -> Dr. {apt.practitioner.first_name} ({apt.status})")
        print(f"    Patient email: {apt.patient.email}")
        print(f"    Practitioner email: {apt.practitioner.email}")
    
    # Test notification functions
    if appointments:
        test_appointment = appointments[0]
        print(f"\n🧪 TESTING WITH APPOINTMENT {test_appointment.id}")
        
        # Test acceptance notification
        print("\n📤 Testing notify_appointment_accepted...")
        try:
            notify_appointment_accepted(test_appointment)
            print("✅ notify_appointment_accepted completed without errors")
        except Exception as e:
            print(f"❌ notify_appointment_accepted failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test cancellation notification
        print("\n📤 Testing notify_appointment_cancelled...")
        try:
            # Temporarily set status to Cancelled for testing
            original_status = test_appointment.status
            test_appointment.status = "Cancelled"
            test_appointment.save()
            
            notify_appointment_cancelled(test_appointment, reason="Test cancellation", cancelled_by="practitioner")
            print("✅ notify_appointment_cancelled completed without errors")
            
            # Restore original status
            test_appointment.status = original_status
            test_appointment.save()
        except Exception as e:
            print(f"❌ notify_appointment_cancelled failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 DEBUG COMPLETE")

if __name__ == "__main__":
    debug_notification_system()