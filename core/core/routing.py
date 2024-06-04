from django.urls import path
from users.consumers import OnlineConsumer
from duels.consumers import DuelConsumer
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/online/<str:token>/', OnlineConsumer.as_asgi()),
    path('ws/duel/<int:duel_id>/', DuelConsumer.as_asgi()),
    path('ws/chat/<int:duel_id>/', ChatConsumer.as_asgi()),
]