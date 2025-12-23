from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from .did_avatar_service import did_service
from .background_removal_service import bg_removal_service

@csrf_exempt
@require_http_methods(["POST"])
def generate_avatar_response(request):
    """Generate D-ID talking avatar video for user message"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Generate AI response text (integrate with your existing AI logic)
        ai_response = generate_ai_response(user_message)
        
        # Generate unique filename
        video_id = str(uuid.uuid4())
        
        # Step 1: Create D-ID talking video
        did_result = did_service.generate_avatar_video(ai_response)
        
        if not did_result or did_result['status'] != 'completed':
            return JsonResponse({
                'error': 'Failed to generate avatar video',
                'fallback_text': ai_response
            }, status=500)
        
        # Step 2: Remove background and convert to WebM
        transparent_video = bg_removal_service.process_did_video(
            did_result['video_url'], 
            video_id
        )
        
        if not transparent_video:
            return JsonResponse({
                'error': 'Failed to process video background',
                'fallback_text': ai_response,
                'original_video': did_result['video_url']
            }, status=500)
        
        # Return success response
        return JsonResponse({
            'success': True,
            'avatar_video': f'/media/avatars/{video_id}.webm',
            'original_video': did_result['video_url'],
            'response_text': ai_response,
            'talk_id': did_result['talk_id']
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'fallback_text': 'I apologize, but I encountered an error. Please try again.'
        }, status=500)

def generate_ai_response(user_message):
    """Generate AI response text (integrate with your existing AI logic)"""
    # This should integrate with your existing AI chatbot logic
    # For now, returning a simple response
    
    responses = {
        'hello': "Hello! I'm your AI medical assistant. How can I help you today?",
        'symptoms': "I can help you understand your symptoms. Please describe what you're experiencing.",
        'appointment': "I can help you schedule an appointment with one of our healthcare providers.",
        'default': "Thank you for your message. I'm here to assist you with your healthcare needs."
    }
    
    message_lower = user_message.lower()
    
    if 'hello' in message_lower or 'hi' in message_lower:
        return responses['hello']
    elif 'symptom' in message_lower or 'pain' in message_lower:
        return responses['symptoms']
    elif 'appointment' in message_lower or 'book' in message_lower:
        return responses['appointment']
    else:
        return responses['default']

@csrf_exempt
@require_http_methods(["GET"])
def get_idle_avatar(request):
    """Return idle/breathing avatar video"""
    # You can pre-generate idle videos for common states
    idle_videos = [
        '/static/avatars/idle_breathing.webm',
        '/static/avatars/idle_blink.webm',
        '/static/avatars/idle_smile.webm'
    ]
    
    import random
    return JsonResponse({
        'idle_video': random.choice(idle_videos)
    })

@csrf_exempt
@require_http_methods(["POST"])
def pregenerate_common_responses(request):
    """Pre-generate videos for common responses"""
    common_responses = [
        "Hello! How can I help you today?",
        "I understand your concern. Let me help you with that.",
        "Thank you for your question. Here's what I recommend.",
        "Please tell me more about your symptoms.",
        "I'm here to assist you with your healthcare needs."
    ]
    
    results = []
    
    for response in common_responses:
        video_id = f"common_{hash(response) % 10000}"
        
        did_result = did_service.generate_avatar_video(response)
        
        if did_result and did_result['status'] == 'completed':
            transparent_video = bg_removal_service.process_did_video(
                did_result['video_url'], 
                video_id
            )
            
            if transparent_video:
                results.append({
                    'text': response,
                    'video': f'/media/avatars/{video_id}.webm'
                })
    
    return JsonResponse({
        'pregenerated': len(results),
        'videos': results
    })