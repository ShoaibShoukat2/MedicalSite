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
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Generate AI response using fallback responses
        ai_response = get_fallback_response(user_message)
        
        # Generate D-ID video (if API key available)
        video_url = None
        if hasattr(settings, 'DID_API_KEY') and settings.DID_API_KEY:
            try:
                video_url = generate_did_video(ai_response)
            except Exception as e:
                print(f"D-ID API error: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'video_url': video_url
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        print(f"Error in ask_avatar: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Server error occurred'
        })

def get_fallback_response(message):
    """Provide fallback responses for common medical questions"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['flu', 'fever', 'cold']):
        return "For flu-like symptoms, rest, stay hydrated, and consider over-the-counter medications. If symptoms persist or worsen, please consult a healthcare provider."
    
    elif any(word in message_lower for word in ['headache', 'head', 'pain']):
        return "Headaches can have various causes. Try rest, hydration, and over-the-counter pain relievers. If headaches are severe or frequent, please see a doctor."
    
    elif any(word in message_lower for word in ['appointment', 'book', 'schedule']):
        return "To book an appointment, please log in to your patient dashboard or call our clinic directly. Our staff will help you find the right specialist and available time slots."
    
    elif any(word in message_lower for word in ['emergency', 'urgent', 'serious']):
        return "For medical emergencies, please call 911 immediately or visit your nearest emergency room. For urgent but non-emergency care, contact our clinic's urgent care line."
    
    elif any(word in message_lower for word in ['specialist', 'doctor', 'physician']):
        return "We have specialists in cardiology, dermatology, orthopedics, neurology, and many other fields. You can browse our doctors on the homepage or through your patient dashboard."
    
    else:
        return "Thank you for your question! For personalized medical advice, I recommend consulting with one of our healthcare professionals. You can book an appointment through our patient portal."

def generate_did_video(text):
    """Generate D-ID talking avatar video"""
    try:
        # D-ID API configuration
        did_api_key = settings.DID_API_KEY
        url = "https://api.d-id.com/talks"
        
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
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            talk_id = response.json().get('id')
            
            # Poll for video completion
            status_url = f"https://api.d-id.com/talks/{talk_id}"
            
            import time
            for _ in range(30):
                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get('status') == 'done':
                        return status_data.get('result_url')
                    elif status_data.get('status') == 'error':
                        break
                time.sleep(1)
        
        return None
        
    except Exception as e:
        print(f"D-ID video generation error: {str(e)}")
        return None

def ai_chat_view(request):
    """Basic AI chat view"""
    return render(request, 'ai_chatbot/ai_chat.html')