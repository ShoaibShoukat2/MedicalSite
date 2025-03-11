from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from .models import ChatRoom, Message
from django.contrib.auth.decorators import login_required

def chat_list(request):
    patient_id = request.session.get('patient_id')
    practitioner_id = request.session.get('practitioner_id')
    
    if not patient_id and not practitioner_id:
        return redirect('login')
    
    user_type = 'patient' if patient_id else 'practitioner'
    user_id = patient_id if patient_id else practitioner_id

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
