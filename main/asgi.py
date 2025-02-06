import os
import django

# Set the Django settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

# Initialize Django BEFORE any imports that use Django features
django.setup()

# Only import after Django is set up
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})