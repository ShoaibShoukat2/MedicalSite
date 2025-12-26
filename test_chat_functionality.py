#!/usr/bin/env python3
"""
Complete Chat System Diagnostic Tool
Run this to comprehensively test your chat system
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from chat.models import ChatRoom, Message
from user_account.models import Patient, Practitioner
from django.utils import timezone
from django.db import connection

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 40)

def test_database_connection():
    print_section("Database Connection Test")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    print_section("Model Accessibility Test")
    try:
        # Test model queries
        chat_rooms = ChatRoom.objects.all()
        messages = Message.objects.all()
        patients = Patient.objects.all()
        practitioners = Practitioner.objects.all()
        
        print(f"✅ Models accessible:")
        print(f"   📊 ChatRooms: {chat_rooms.count()}")
        print(f"   💬 Messages: {messages.count()}")
        print(f"   👤 Patients: {patients.count()}")
        print(f"   👨‍⚕️ Practitioners: {practitioners.count()}")
        
        return True
    except Exception as e:
        print(f"❌ Error accessing models: {e}")
        return False

def test_recent_activity():
    print_section("Recent Activity Analysis")
    try:
        # Recent messages
        recent_messages = Message.objects.order_by('-timestamp')[:10]
        print(f"📝 Recent Messages ({recent_messages.count()}):")
        
        if recent_messages:
            for i, msg in enumerate(recent_messages, 1):
                time_ago = timezone.now() - msg.timestamp
                print(f"   {i}. {msg.sender_type}: {msg.content[:40]}... ({time_ago.days}d {time_ago.seconds//3600}h ago)")
        else:
            print("   No messages found")
        
        # Active chat rooms
        active_rooms = ChatRoom.objects.filter(messages__isnull=False).distinct()
        print(f"\n💬 Active Chat Rooms ({active_rooms.count()}):")
        
        for room in active_rooms[:5]:
            msg_count = room.messages.count()
            last_msg = room.messages.order_by('-timestamp').first()
            patient_name = f"{room.patient.first_name} {room.patient.last_name}"
            practitioner_name = f"Dr. {room.practitioner.first_name} {room.practitioner.last_name}"
            
            print(f"   🏥 {patient_name} ↔ {practitioner_name}")
            print(f"      Messages: {msg_count}, Last: {last_msg.timestamp if last_msg else 'None'}")
        
        return True
    except Exception as e:
        print(f"❌ Error analyzing recent activity: {e}")
        return False

def test_message_integrity():
    print_section("Message Integrity Check")
    try:
        # Check for orphaned messages
        orphaned_messages = Message.objects.filter(chat_room__isnull=True)
        print(f"🔍 Orphaned messages: {orphaned_messages.count()}")
        
        # Check for messages without sender info
        from django.db import models
        invalid_messages = Message.objects.filter(
            models.Q(sender_type__isnull=True) | 
            models.Q(sender_id__isnull=True)
        )
        print(f"🔍 Invalid sender info: {invalid_messages.count()}")
        
        # Check unread messages
        unread_messages = Message.objects.filter(is_read=False)
        print(f"📬 Unread messages: {unread_messages.count()}")
        
        if unread_messages.exists():
            print("   Recent unread:")
            for msg in unread_messages[:3]:
                print(f"   - From {msg.sender_type} in room {msg.chat_room.id}: {msg.content[:30]}...")
        
        # Check message distribution
        patient_messages = Message.objects.filter(sender_type='patient').count()
        practitioner_messages = Message.objects.filter(sender_type='practitioner').count()
        
        print(f"\n📊 Message Distribution:")
        print(f"   👤 Patient messages: {patient_messages}")
        print(f"   👨‍⚕️ Practitioner messages: {practitioner_messages}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking message integrity: {e}")
        return False

def test_user_data():
    print_section("User Data Analysis")
    try:
        # Check patients
        patients = Patient.objects.all()
        patients_with_chats = Patient.objects.filter(chatrooms__isnull=False).distinct()
        
        print(f"👤 Patients:")
        print(f"   Total: {patients.count()}")
        print(f"   With chats: {patients_with_chats.count()}")
        
        if patients.exists():
            print("   Sample patients:")
            for patient in patients[:3]:
                chat_count = patient.chatrooms.count()
                print(f"   - {patient.first_name} {patient.last_name} ({chat_count} chats)")
        
        # Check practitioners
        practitioners = Practitioner.objects.all()
        practitioners_with_chats = Practitioner.objects.filter(chatrooms__isnull=False).distinct()
        
        print(f"\n👨‍⚕️ Practitioners:")
        print(f"   Total: {practitioners.count()}")
        print(f"   With chats: {practitioners_with_chats.count()}")
        
        if practitioners.exists():
            print("   Sample practitioners:")
            for practitioner in practitioners[:3]:
                chat_count = practitioner.chatrooms.count()
                print(f"   - Dr. {practitioner.first_name} {practitioner.last_name} ({chat_count} chats)")
        
        return True
    except Exception as e:
        print(f"❌ Error analyzing user data: {e}")
        return False

def create_test_data():
    print_section("Creating Test Data")
    try:
        # Get or create test users
        patient = Patient.objects.first()
        practitioner = Practitioner.objects.first()
        
        if not patient:
            print("⚠️  No patients found. Creating test patient...")
            patient = Patient.objects.create(
                first_name="Test",
                last_name="Patient",
                email="test.patient@example.com",
                phone="1234567890"
            )
            print(f"✅ Created test patient: {patient.first_name} {patient.last_name}")
        
        if not practitioner:
            print("⚠️  No practitioners found. Creating test practitioner...")
            practitioner = Practitioner.objects.create(
                first_name="Test",
                last_name="Doctor",
                email="test.doctor@example.com",
                phone="0987654321",
                doctor_type="General Practice"
            )
            print(f"✅ Created test practitioner: Dr. {practitioner.first_name} {practitioner.last_name}")
        
        # Get or create chat room
        chat_room, created = ChatRoom.objects.get_or_create(
            patient=patient,
            practitioner=practitioner
        )
        
        if created:
            print(f"✅ Created new chat room: {chat_room.id}")
        else:
            print(f"✅ Using existing chat room: {chat_room.id}")
        
        # Create test messages
        test_messages = [
            ("patient", "Hello doctor, I have a question about my medication."),
            ("practitioner", "Hello! I'd be happy to help. What's your question?"),
            ("patient", "I'm experiencing some side effects. Is this normal?"),
            ("practitioner", "Can you describe the side effects you're experiencing?"),
            ("patient", "I feel a bit dizzy and nauseous."),
            ("practitioner", "Those can be common side effects. How long have you been experiencing them?"),
            ("patient", "About 3 days now."),
            ("practitioner", "I recommend reducing the dosage. Let's schedule a follow-up."),
        ]
        
        created_count = 0
        for sender_type, content in test_messages:
            sender_id = patient.id if sender_type == 'patient' else practitioner.id
            
            # Check if message already exists
            if not Message.objects.filter(
                chat_room=chat_room,
                sender_type=sender_type,
                content=content
            ).exists():
                Message.objects.create(
                    chat_room=chat_room,
                    sender_type=sender_type,
                    sender_id=sender_id,
                    content=content
                )
                created_count += 1
        
        print(f"✅ Created {created_count} new test messages")
        print(f"📊 Total messages in test chat: {chat_room.messages.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def test_chat_functionality():
    print_section("Chat Functionality Test")
    try:
        # Test message creation
        patient = Patient.objects.first()
        practitioner = Practitioner.objects.first()
        
        if not patient or not practitioner:
            print("❌ No test users available")
            return False
        
        chat_room = ChatRoom.objects.filter(
            patient=patient,
            practitioner=practitioner
        ).first()
        
        if not chat_room:
            print("❌ No test chat room available")
            return False
        
        # Test message creation
        test_message = Message.objects.create(
            chat_room=chat_room,
            sender_type='patient',
            sender_id=patient.id,
            content=f"Test message created at {timezone.now()}"
        )
        
        print(f"✅ Successfully created test message: {test_message.id}")
        
        # Test message retrieval
        messages = chat_room.messages.all().order_by('timestamp')
        print(f"✅ Retrieved {messages.count()} messages from chat room")
        
        # Test unread message functionality
        unread_count = chat_room.messages.filter(
            is_read=False,
            sender_type='practitioner'
        ).count()
        print(f"✅ Unread messages for patient: {unread_count}")
        
        # Clean up test message
        test_message.delete()
        print("✅ Cleaned up test message")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat functionality: {e}")
        return False

def generate_report():
    print_section("System Health Report")
    
    # Overall statistics
    total_rooms = ChatRoom.objects.count()
    total_messages = Message.objects.count()
    total_patients = Patient.objects.count()
    total_practitioners = Practitioner.objects.count()
    
    # Activity statistics
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    messages_today = Message.objects.filter(timestamp__date=today).count()
    messages_yesterday = Message.objects.filter(timestamp__date=yesterday).count()
    messages_week = Message.objects.filter(timestamp__date__gte=week_ago).count()
    
    print(f"📊 System Statistics:")
    print(f"   Total Chat Rooms: {total_rooms}")
    print(f"   Total Messages: {total_messages}")
    print(f"   Total Patients: {total_patients}")
    print(f"   Total Practitioners: {total_practitioners}")
    
    print(f"\n📈 Activity Statistics:")
    print(f"   Messages today: {messages_today}")
    print(f"   Messages yesterday: {messages_yesterday}")
    print(f"   Messages this week: {messages_week}")
    
    # Health indicators
    health_score = 0
    max_score = 5
    
    if total_rooms > 0:
        health_score += 1
    if total_messages > 0:
        health_score += 1
    if total_patients > 0:
        health_score += 1
    if total_practitioners > 0:
        health_score += 1
    if Message.objects.filter(chat_room__isnull=True).count() == 0:
        health_score += 1
    
    health_percentage = (health_score / max_score) * 100
    
    print(f"\n🏥 System Health: {health_percentage:.0f}% ({health_score}/{max_score})")
    
    if health_percentage >= 80:
        print("✅ System is healthy and ready for use")
    elif health_percentage >= 60:
        print("⚠️  System has minor issues but is functional")
    else:
        print("❌ System has significant issues that need attention")

def main():
    print_header("COMPLETE CHAT SYSTEM DIAGNOSTIC")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Database Connection", test_database_connection),
        ("Model Accessibility", test_models),
        ("Recent Activity", test_recent_activity),
        ("Message Integrity", test_message_integrity),
        ("User Data", test_user_data),
        ("Chat Functionality", test_chat_functionality),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Ask about test data
    print_section("Test Data Creation")
    create_test = input("❓ Do you want to create/update test data? (y/n): ").lower().strip()
    if create_test == 'y':
        results["Test Data Creation"] = create_test_data()
    
    # Generate final report
    generate_report()
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Next Steps:")
    if passed_tests == total_tests:
        print("1. ✅ All tests passed! Your chat system is ready")
        print("2. 🌐 Open test_complete_chat.html to test the UI")
        print("3. 🚀 Test your actual Django chat interface")
    else:
        print("1. 🔧 Fix the failing tests above")
        print("2. 📋 Check your Django settings and database")
        print("3. 🔄 Run this diagnostic again")
    
    print("4. 📖 Check the Django server logs for any errors")
    print("5. 🧪 Use the debug files for UI testing")
    
    print(f"\n🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()