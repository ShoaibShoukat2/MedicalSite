from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    # HTTP-based message endpoints (fallback for WebSocket issues)
    path('send-message/', views.send_message_http, name='send_message_http'),
    path('get-messages/<int:room_id>/', views.get_messages_http, name='get_messages_http'),
    path('messages/<int:room_id>/', views.get_messages_http, name='get_messages_api'),  # Alternative endpoint
    # New endpoints for open messaging
    path('browse-doctors/', views.browse_practitioners, name='browse_practitioners'),
    path('start-chat/', views.start_chat_with_practitioner, name='start_chat_with_practitioner'),
]