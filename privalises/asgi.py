import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import posts.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privalises.settings')

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            posts.routing.websocket_urlpatterns
        )
    ),
})