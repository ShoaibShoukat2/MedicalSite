from django.urls import re_path

# Import consumers after django.setup() is called
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]