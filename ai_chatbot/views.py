from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import os
from django.conf import settings

@csrf_exempt
@require_http_methods(["POST"])
def ask_avatar(request):
    """Handle AI avatar questions with D-ID video generation"""
    print("\n" + "=" * 80)
    print("🎬 AVATAR VIDEO GENERATION REQUEST")
    print("=" * 80)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        print(f"📝 Message received: {user_message}")
        
        if not user_message:
            print("❌ ERROR: Message is empty")
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Generate AI response using fallback responses
        print("🤖 Generating AI response...")
        ai_response = get_fallback_response(user_message)
        print(f"✅ AI Response: {ai_response[:100]}...")
        
        # Generate D-ID video (if API key available)
        video_url = None
        if hasattr(settings, 'DID_API_KEY') and settings.DID_API_KEY:
            print("🎥 D-ID API key found, attempting video generation...")
            try:
                video_url = generate_did_video(ai_response)
                if video_url:
                    print(f"✅ D-ID video generated successfully!")
                    print(f"🔗 Video URL: {video_url}")
                else:
                    print("⚠️ D-ID video generation returned None")
            except Exception as e:
                print(f"❌ D-ID API error: {str(e)}")
        else:
            print("⚠️ D-ID API key not configured, skipping video generation")
        
        response_data = {
            'success': True,
            'response': ai_response,
            'video_url': video_url
        }
        print(f"📤 Sending response to client")
        print("=" * 80 + "\n")
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid JSON data")
        print("=" * 80 + "\n")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        print(f"❌ ERROR in ask_avatar: {str(e)}")
        print("=" * 80 + "\n")
        return JsonResponse({
            'success': False,
            'error': 'Server error occurred'
        })

def get_fallback_response(message):
    """Provide fallback responses for common medical questions"""
    print(f"   🔄 Generating fallback response for: {message[:50]}...")
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['flu', 'fever', 'cold']):
        print(f"   ✅ Category matched: Flu/Fever/Cold")
        return "For flu-like symptoms, rest, stay hydrated, and consider over-the-counter medications. If symptoms persist or worsen, please consult a healthcare provider."
    
    elif any(word in message_lower for word in ['headache', 'head', 'pain']):
        print(f"   ✅ Category matched: Headache/Pain")
        return "Headaches can have various causes. Try rest, hydration, and over-the-counter pain relievers. If headaches are severe or frequent, please see a doctor."
    
    elif any(word in message_lower for word in ['appointment', 'book', 'schedule']):
        print(f"   ✅ Category matched: Appointment")
        return "To book an appointment, please log in to your patient dashboard or call our clinic directly. Our staff will help you find the right specialist and available time slots."
    
    elif any(word in message_lower for word in ['emergency', 'urgent', 'serious']):
        print(f"   ✅ Category matched: Emergency")
        return "For medical emergencies, please call 911 immediately or visit your nearest emergency room. For urgent but non-emergency care, contact our clinic's urgent care line."
    
    elif any(word in message_lower for word in ['specialist', 'doctor', 'physician']):
        print(f"   ✅ Category matched: Specialist")
        return "We have specialists in cardiology, dermatology, orthopedics, neurology, and many other fields. You can browse our doctors on the homepage or through your patient dashboard."
    
    else:
        print(f"   ✅ Using default response")
        return "Thank you for your question! For personalized medical advice, I recommend consulting with one of our healthcare professionals. You can book an appointment through our patient portal."

def generate_did_video(text):
    """Generate D-ID talking avatar video"""
    print("\n   " + "-" * 70)
    print("   🎬 D-ID VIDEO GENERATION STARTED")
    print("   " + "-" * 70)
    
    try:
        # D-ID API configuration
        did_api_key = settings.DID_API_KEY
        url = "https://api.d-id.com/talks"
        
        print(f"   🔑 API Key configured: {did_api_key[:10]}...")
        print(f"   🌐 API URL: {url}")
        print(f"   📝 Text to speak: {text[:100]}...")
        
        headers = {
            "Authorization": f"Basic {did_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use a professional medical avatar image
        payload = {
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JennyNeural"
                }
            },
            "source_url": "https://res.cloudinary.com/dovwzsl4v/image/upload/v1752823658/avatar_zfdfcr.jpg",
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            }
        }
        
        print(f"   📤 Sending request to D-ID API...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"   📡 Response status code: {response.status_code}")
        
        if response.status_code == 201:
            talk_id = response.json().get('id')
            print(f"   ✅ Talk created successfully! ID: {talk_id}")
            
            # Poll for video completion
            status_url = f"https://api.d-id.com/talks/{talk_id}"
            print(f"   ⏳ Polling for video completion...")
            
            import time
            for attempt in range(30):
                print(f"   🔄 Attempt {attempt + 1}/30...")
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get('status')
                    print(f"   📊 Current status: {current_status}")
                    
                    if current_status == 'done':
                        video_url = status_data.get('result_url')
                        print(f"   ✅ VIDEO READY!")
                        print(f"   🔗 Video URL: {video_url}")
                        print("   " + "-" * 70 + "\n")
                        return video_url
                    elif current_status == 'error':
                        print(f"   ❌ D-ID reported error status")
                        break
                else:
                    print(f"   ⚠️ Status check failed: {status_response.status_code}")
                    
                time.sleep(1)
            
            print(f"   ⚠️ Video generation timed out after 30 seconds")
        else:
            print(f"   ❌ Failed to create talk: {response.text}")
        
        print("   " + "-" * 70 + "\n")
        return None
        
    except Exception as e:
        print(f"   ❌ D-ID video generation error: {str(e)}")
        print("   " + "-" * 70 + "\n")
        return None

def ai_chat_view(request):
    """Basic AI chat view"""
    return render(request, 'ai_chatbot/ai_chat.html')