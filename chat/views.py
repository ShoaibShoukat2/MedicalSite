from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatRoom, Message
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone

def chat_list(request):
    patient_id = request.session.get('patient_id')
    practitioner_id = request.session.get('practitioner_id')
    
    if not patient_id and not practitioner_id:
        return redirect('frontend:patient_login')
    
    user_type = 'patient' if patient_id else 'practitioner'
    user_id = patient_id if patient_id else practitioner_id

    try:
        if user_type == 'patient':
            chat_rooms = ChatRoom.objects.filter(patient_id=user_id)
        else:
            chat_rooms = ChatRoom.objects.filter(practitioner_id=user_id)

        messages = Message.objects.filter(chat_room__in=chat_rooms).order_by('-timestamp')
        chat_rooms = chat_rooms.prefetch_related(
            Prefetch('messages', queryset=messages, to_attr='last_messages')
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__is_read=False,
                    messages__sender_type='patient' if user_type == 'practitioner' else 'practitioner'
                )
            )
        ).order_by('-updated_at')

        context = {
            'chat_rooms': chat_rooms,
            'user_type': user_type,
            'user_id': user_id
        }
        
        return render(request, 'chat/chat_list.html', context)
    except Exception as e:
        print(f"Error in chat_list: {str(e)}")
        return render(request, 'chat/error.html', {
            'error_message': 'Unable to load chat list. Please try again.'
        })

def chat_room(request, room_id):
    patient_id = request.session.get('patient_id')
    practitioner_id = request.session.get('practitioner_id')
    
    if not patient_id and not practitioner_id:
        return redirect('login')
    
    user_id = patient_id if patient_id else practitioner_id
    user_type = 'patient' if patient_id else 'practitioner'
    
    try:
        chat_room = get_object_or_404(
            ChatRoom.objects.filter(
                Q(patient_id=user_id) | Q(practitioner_id=user_id),
                id=room_id
            )
        )
     
        if user_type == 'patient':
            chat_room.other_user = chat_room.practitioner
        else:
            chat_room.other_user = chat_room.patient
        
        messages = chat_room.messages.all().order_by('timestamp')
        
        unread_messages = messages.filter(
            is_read=False,
            sender_type='practitioner' if user_type == 'patient' else 'patient'
        )
        unread_messages.update(is_read=True)
        
        context = {
            'chat_room': chat_room,
            'messages': messages,
            'user_id': user_id,
            'user_type': user_type
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'chat/chat_room_content.html', context)
        
        chat_rooms = ChatRoom.objects.filter(
            Q(patient_id=user_id) | Q(practitioner_id=user_id)
        ).prefetch_related('messages')
        
        context.update({
            'chat_rooms': chat_rooms,
            'active_room_id': room_id
        })
        
        return render(request, 'chat/chat_list.html', context)
        
    except Exception as e:
        print(f"Error in chat_room view: {str(e)}")
        return render(request, 'chat/error.html', {
            'error_message': 'Unable to load chat room. Please try again.'
        }, status=500)

# HTTP-based message sending (fallback for WebSocket issues)
@csrf_exempt
@require_http_methods(["POST"])
def send_message_http(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        
        # Get user info from session
        patient_id = request.session.get('patient_id')
        practitioner_id = request.session.get('practitioner_id')
        
        if not (patient_id or practitioner_id):
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        # Determine user type and ID
        if patient_id:
            user_type = 'patient'
            user_id = patient_id
        else:
            user_type = 'practitioner'
            user_id = practitioner_id
        
        # Get chat room and verify access
        try:
            if user_type == 'patient':
                chat_room = ChatRoom.objects.get(id=room_id, patient_id=user_id)
            else:
                chat_room = ChatRoom.objects.get(id=room_id, practitioner_id=user_id)
        except ChatRoom.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chat room not found or access denied'})
        
        # Create message
        message = Message.objects.create(
            chat_room=chat_room,
            sender_type=user_type,
            sender_id=user_id,
            content=message_content
        )
        
        # Update chat room timestamp
        chat_room.updated_at = timezone.now()
        chat_room.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_type': message.sender_type,
                'sender_id': message.sender_id,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'full_timestamp': message.timestamp.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Error in send_message_http: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error occurred'})

# Get latest messages for a room
@require_http_methods(["GET"])
def get_messages_http(request, room_id):
    try:
        # Get user info from session
        patient_id = request.session.get('patient_id')
        practitioner_id = request.session.get('practitioner_id')
        
        if not (patient_id or practitioner_id):
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        # Determine user type and ID
        if patient_id:
            user_type = 'patient'
            user_id = patient_id
        else:
            user_type = 'practitioner'
            user_id = practitioner_id
        
        # Get chat room and verify access
        try:
            if user_type == 'patient':
                chat_room = ChatRoom.objects.get(id=room_id, patient_id=user_id)
            else:
                chat_room = ChatRoom.objects.get(id=room_id, practitioner_id=user_id)
        except ChatRoom.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chat room not found or access denied'})
        
        # Get messages
        messages = chat_room.messages.all().order_by('timestamp')
        
        # Mark unread messages as read
        unread_messages = messages.filter(
            is_read=False,
            sender_type='practitioner' if user_type == 'patient' else 'patient'
        )
        unread_messages.update(is_read=True)
        
        # Format messages
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_type': message.sender_type,
                'sender_id': message.sender_id,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'full_timestamp': message.timestamp.isoformat(),
                'is_read': message.is_read
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'user_type': user_type,
            'user_id': user_id
        })
        
    except Exception as e:
        print(f"Error in get_messages_http: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error occurred'})
