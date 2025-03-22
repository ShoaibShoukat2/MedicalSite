import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()  # Ensure Django is initialized before importing other modules

# Now import WebSocket routes after `django.setup()`
import chat.routing
import ai_chatbot.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns +
                ai_chatbot.routing.websocket_urlpatterns
            )
        )
    ),
})



