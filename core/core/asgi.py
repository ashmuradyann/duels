import os
from django.core.asgi import get_asgi_application
from django.urls import re_path, path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django_nextjs.proxy import NextJSProxyHttpConsumer, NextJSProxyWebsocketConsumer
from django.conf import settings
from django.utils.module_loading import import_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()

http_routes = [re_path(r"", django_asgi_app)]
websocket_routers = import_string('core.routing.websocket_urlpatterns')

if settings.DEBUG:
    re_path_pattern = r"^(?:_next|__next|next|support|duels|img|fonts).*"
    http_routes.insert(0, re_path(re_path_pattern, NextJSProxyHttpConsumer.as_asgi()))
    websocket_routers.insert(0, path("_next/webpack-hmr", NextJSProxyWebsocketConsumer.as_asgi()))

application = ProtocolTypeRouter({
    "http": URLRouter(http_routes),
    'websocket': AuthMiddlewareStack(URLRouter(websocket_routers)),
})