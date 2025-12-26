from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatRoom, Message
from user_account.models import Patient, Practitioner
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
        # Get user object for template context
        if user_type == 'patient':
            user = Patient.objects.get(id=user_id)
            chat_rooms = ChatRoom.objects.filter(patient_id=user_id)
        else:
            user = Practitioner.objects.get(id=user_id)
            chat_rooms = ChatRoom.objects.filter(practitioner_id=user_id)

        # Get latest messages for each chat room
        messages = Message.objects.filter(chat_room__in=chat_rooms).order_by('-timestamp')
        
        # Prefetch related data and calculate unread counts
        chat_rooms = chat_rooms.select_related('patient', 'practitioner').prefetch_related(
            Prefetch('messages', queryset=messages[:1], to_attr='last_messages')
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
            'user_id': user_id,
            'user': user
        }
        
        # Use different templates based on user type
        if user_type == 'patient':
            template_name = 'chat/patient_chat_list.html'
        else:
            template_name = 'chat/practitioner_chat_list.html'
        
        return render(request, template_name, context)
        
    except Patient.DoesNotExist:
        return render(request, 'chat/error.html', {
            'error_message': 'Patient account not found. Please log in again.'
        })
    except Practitioner.DoesNotExist:
        return render(request, 'chat/error.html', {
            'error_message': 'Practitioner account not found. Please log in again.'
        })
    except Exception as e:
        print(f"Error in chat_list: {str(e)}")
        return render(request, 'chat/error.html', {
            'error_message': 'Unable to load chat list. Please try again.'
        })

def chat_room(request, room_id):
    patient_id = request.session.get('patient_id')
    practitioner_id = request.session.get('practitioner_id')
    
    if not patient_id and not practitioner_id:
        return redirect('frontend:patient_login')
    
    user_id = patient_id if patient_id else practitioner_id
    user_type = 'patient' if patient_id else 'practitioner'
    
    try:
        # Check if chat room exists and user has access
        if user_type == 'patient':
            chat_room = get_object_or_404(ChatRoom, id=room_id, patient_id=user_id)
            chat_room.other_user = chat_room.practitioner
        else:
            chat_room = get_object_or_404(ChatRoom, id=room_id, practitioner_id=user_id)
            chat_room.other_user = chat_room.patient
        
        messages = chat_room.messages.all().order_by('timestamp')
        
        # Mark unread messages as read
        unread_messages = messages.filter(
            is_read=False,
            sender_type='practitioner' if user_type == 'patient' else 'patient'
        )
        unread_count = unread_messages.count()
        if unread_count > 0:
            unread_messages.update(is_read=True)
        
        context = {
            'chat_room': chat_room,
            'messages': messages,
            'user_id': user_id,
            'user_type': user_type
        }

        # If this is an AJAX request, return only the chat room content
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'chat/chat_room_content.html', context)
        
        # For regular requests, return the full chat list with active room
        # Get all chat rooms for sidebar
        if user_type == 'patient':
            chat_rooms = ChatRoom.objects.filter(patient_id=user_id)
        else:
            chat_rooms = ChatRoom.objects.filter(practitioner_id=user_id)
            
        # Get latest messages for each chat room
        messages_query = Message.objects.filter(chat_room__in=chat_rooms).order_by('-timestamp')
        
        # Prefetch related data and calculate unread counts
        chat_rooms = chat_rooms.select_related('patient', 'practitioner').prefetch_related(
            Prefetch('messages', queryset=messages_query[:1], to_attr='last_messages')
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(
                    messages__is_read=False,
                    messages__sender_type='patient' if user_type == 'practitioner' else 'practitioner'
                )
            )
        ).order_by('-updated_at')
        
        # Get user object for template context
        if user_type == 'patient':
            user = Patient.objects.get(id=user_id)
        else:
            user = Practitioner.objects.get(id=user_id)
        
        context.update({
            'chat_rooms': chat_rooms,
            'active_room_id': room_id,
            'user': user
        })
        
        # Use different templates based on user type
        if user_type == 'patient':
            template_name = 'chat/patient_chat_list.html'
        else:
            template_name = 'chat/practitioner_chat_list.html'
        
        return render(request, template_name, context)
        
    except ChatRoom.DoesNotExist:
        return render(request, 'chat/error.html', {
            'error_message': 'Chat room not found or you do not have permission to access it.'
        }, status=404)
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

def browse_practitioners(request):
    """View for patients to browse and message practitioners"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return redirect('frontend:patient_login')
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Get all practitioners
        practitioners = Practitioner.objects.filter(
            photo__isnull=False,
            price__isnull=False,
            description__isnull=False
        ).exclude(
            photo='',
            price=0,
            description=''
        )
        
        # Get existing chat rooms for this patient
        existing_chats = ChatRoom.objects.filter(patient=patient).values_list('practitioner_id', flat=True)
        
        # Add chat status to practitioners
        for practitioner in practitioners:
            practitioner.has_chat = practitioner.id in existing_chats
            if practitioner.has_chat:
                chat_room = ChatRoom.objects.get(patient=patient, practitioner=practitioner)
                practitioner.chat_room_id = chat_room.id
                # Get unread message count
                practitioner.unread_count = Message.objects.filter(
                    chat_room=chat_room,
                    sender_type='practitioner',
                    is_read=False
                ).count()
            else:
                practitioner.unread_count = 0
        
        context = {
            'practitioners': practitioners,
            'patient': patient,
        }
        
        return render(request, 'chat/browse_practitioners.html', context)
        
    except Exception as e:
        print(f"Error in browse_practitioners: {str(e)}")
        return render(request, 'chat/error.html', {
            'error_message': 'Unable to load practitioners. Please try again.'
        })

@csrf_exempt
@require_http_methods(["POST"])
def start_chat_with_practitioner(request):
    """API endpoint for patients to start a chat with a practitioner"""
    patient_id = request.session.get('patient_id')
    
    if not patient_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = json.loads(request.body)
        practitioner_id = data.get('practitioner_id')
        
        if not practitioner_id:
            return JsonResponse({'success': False, 'error': 'Practitioner ID required'})
        
        patient = get_object_or_404(Patient, id=patient_id)
        practitioner = get_object_or_404(Practitioner, id=practitioner_id)
        
        # Get or create chat room
        chat_room, created = ChatRoom.objects.get_or_create(
            patient=patient,
            practitioner=practitioner
        )
        
        # Send initial message if this is a new chat
        if created:
            Message.objects.create(
                chat_room=chat_room,
                sender_type='patient',
                sender_id=patient_id,
                content=f"Hello Dr. {practitioner.first_name}, I would like to consult with you."
            )
        
        return JsonResponse({
            'success': True,
            'chat_room_id': chat_room.id,
            'created': created,
            'practitioner_name': f"Dr. {practitioner.first_name} {practitioner.last_name}",
            'message': 'Chat started successfully!' if created else 'Chat room already exists.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        print(f"Error in start_chat_with_practitioner: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error occurred'})