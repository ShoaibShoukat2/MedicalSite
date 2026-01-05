#!/usr/bin/env python3
"""
Test Chat Endpoints
Run this to test if your chat endpoints are working properly
"""

import os
import sys
import django
import requests
from django.test import Client
from django.urls import reverse

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from chat.models import ChatRoom, Message
from user_account.models import Patient, Practitioner
from django.contrib.sessions.models import Session

def test_chat_endpoints():
    print("🔍 Testing Chat Endpoints...")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Test 1: Check if chat URLs are accessible
    try:
        print("\n📋 Testing URL patterns...")
        
        # Test chat list URL
        response = client.get('/chat/')
        print(f"  - Chat list (/chat/): Status {response.status_code}")
        
        # Test with a sample room ID
        if ChatRoom.objects.exists():
            room = ChatRoom.objects.first()
            response = client.get(f'/chat/room/{room.id}/')
            print(f"  - Chat room (/chat/room/{room.id}/): Status {response.status_code}")
            
            # Test AJAX request
            response = client.get(f'/chat/room/{room.id}/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            print(f"  - Chat room AJAX: Status {response.status_code}")
            
        else:
            print("  - No chat rooms found for testing")
            
    except Exception as e:
        print(f"❌ Error testing URLs: {e}")
    
    # Test 2: Check session handling
    try:
        print("\n🔐 Testing session handling...")
        
        # Check if we have test users
        patients = Patient.objects.all()[:3]
        practitioners = Practitioner.objects.all()[:3]
        
        print(f"  - Available patients: {patients.count()}")
        print(f"  - Available practitioners: {practitioners.count()}")
        
        if patients.exists():
            patient = patients.first()
            # Simulate patient session
            session = client.session
            session['patient_id'] = patient.id
            session.save()
            
            response = client.get('/chat/')
            print(f"  - Patient chat access: Status {response.status_code}")
            
        if practitioners.exists():
            practitioner = practitioners.first()
            # Simulate practitioner session
            session = client.session
            session.clear()
            session['practitioner_id'] = practitioner.id
            session.save()
            
            response = client.get('/chat/')
            print(f"  - Practitioner chat access: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing sessions: {e}")
    
    # Test 3: Check message sending endpoint
    try:
        print("\n📤 Testing message sending...")
        
        if ChatRoom.objects.exists() and practitioners.exists():
            room = ChatRoom.objects.first()
            practitioner = practitioners.first()
            
            # Set practitioner session
            session = client.session
            session.clear()
            session['practitioner_id'] = practitioner.id
            session.save()
            
            # Test message sending
            response = client.post('/chat/send-message/', 
                                 data={'room_id': room.id, 'message': 'Test message'},
                                 content_type='application/json')
            print(f"  - Send message endpoint: Status {response.status_code}")
            
            # Test get messages
            response = client.get(f'/chat/messages/{room.id}/')
            print(f"  - Get messages endpoint: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing message endpoints: {e}")
    
    # Test 4: Check template rendering
    try:
        print("\n🎨 Testing template rendering...")
        
        if practitioners.exists():
            practitioner = practitioners.first()
            session = client.session
            session.clear()
            session['practitioner_id'] = practitioner.id
            session.save()
            
            response = client.get('/chat/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for key elements
                checks = [
                    ('chat-sidebar', 'id="chat-sidebar"' in content),
                    ('chat-area', 'id="chat-area"' in content),
                    ('chat-room-container', 'id="chat-room-container"' in content),
                    ('loadChatRoom function', 'function loadChatRoom' in content),
                    ('JavaScript', '<script>' in content),
                ]
                
                for check_name, result in checks:
                    status = "✅ Found" if result else "❌ Missing"
                    print(f"  - {check_name}: {status}")
            else:
                print(f"  - Template rendering failed: Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing templates: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Endpoint testing completed!")

def check_javascript_errors():
    print("\n🔍 Checking for common JavaScript issues...")
    print("-" * 40)
    
    try:
        # Read the practitioner template
        with open('chat/templates/chat/practitioner_chat_list.html', 'r') as f:
            content = f.read()
            
        # Check for common issues
        issues = []
        
        if 'loadChatRoom' not in content:
            issues.append("loadChatRoom function not found")
            
        if 'chat-room-container' not in content:
            issues.append("chat-room-container element not found")
            
        if 'fetch(' not in content:
            issues.append("fetch API calls not found")
            
        if 'addEventListener' not in content:
            issues.append("Event listeners not found")
            
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No obvious JavaScript issues found")
            
    except FileNotFoundError:
        print("❌ Template file not found")
    except Exception as e:
        print(f"❌ Error checking JavaScript: {e}")

def generate_debug_info():
    print("\n📊 Debug Information")
    print("-" * 40)
    
    try:
        # Database info
        total_rooms = ChatRoom.objects.count()
        total_messages = Message.objects.count()
        total_patients = Patient.objects.count()
        total_practitioners = Practitioner.objects.count()
        
        print(f"Database Status:")
        print(f"  - Chat Rooms: {total_rooms}")
        print(f"  - Messages: {total_messages}")
        print(f"  - Patients: {total_patients}")
        print(f"  - Practitioners: {total_practitioners}")
        
        # Sample data
        if total_rooms > 0:
            print(f"\nSample Chat Rooms:")
            for room in ChatRoom.objects.all()[:3]:
                msg_count = room.messages.count()
                print(f"  - Room {room.id}: {room.patient.first_name} ↔ Dr. {room.practitioner.first_name} ({msg_count} messages)")
        
        # Recent activity
        recent_messages = Message.objects.order_by('-timestamp')[:5]
        if recent_messages:
            print(f"\nRecent Messages:")
            for msg in recent_messages:
                print(f"  - {msg.sender_type}: {msg.content[:30]}... ({msg.timestamp})")
                
    except Exception as e:
        print(f"❌ Error generating debug info: {e}")

def main():
    print("🚀 Chat System Endpoint Testing")
    print("=" * 60)
    
    # Run tests
    test_chat_endpoints()
    check_javascript_errors()
    generate_debug_info()
    
    print(f"\n🎯 Troubleshooting Steps:")
    print("1. Check Django server logs for errors")
    print("2. Open browser developer tools and check console")
    print("3. Verify CSRF tokens are present")
    print("4. Test with debug_chat_loading.html")
    print("5. Check network tab for failed requests")
    
    print(f"\n📋 Common Issues:")
    print("- Missing session data (patient_id or practitioner_id)")
    print("- CSRF token mismatch")
    print("- JavaScript errors preventing event handlers")
    print("- Missing DOM elements (chat-room-container)")
    print("- Network connectivity issues")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()