from django.urls import path
from .consumers import AIChatConsumer

websocket_urlpatterns = [
    path('ws/ai-chat/', AIChatConsumer.as_asgi()),
]


