from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
     path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    # HTTP-based message endpoints (fallback for WebSocket issues)
    path('send-message/', views.send_message_http, name='send_message_http'),
    path('get-messages/<int:room_id>/', views.get_messages_http, name='get_messages_http'),
]