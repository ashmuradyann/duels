import os
import pytest
import asyncio
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.testing import WebsocketCommunicator
from asgiref.sync import sync_to_async

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from rest_framework.test import APIClient
from core.routing import websocket_urlpatterns
from users.models import CustomUser
from .models import Duels, Maps

@pytest.mark.asyncio
async def test_create_socket():
    try:
        user1 = await sync_to_async(CustomUser.objects.get)(username='test_user_1')
    except CustomUser.DoesNotExist:
        user1 = await sync_to_async(CustomUser.objects.create)(username='test_user_1', password='password', balance=1000)

    try:
        user2 = await sync_to_async(CustomUser.objects.get)(username='test_user_2')
    except CustomUser.DoesNotExist:
        user2 = await sync_to_async(CustomUser.objects.create)(username='test_user_2', password='password', balance=1000)
    map_object = await sync_to_async(Maps.objects.create)(name='Test Map', image='test_map.jpg')
    open_duel = await sync_to_async(Duels.objects.create)(status='open', bet=100, player_1=user1, map_name=map_object)

    application = ProtocolTypeRouter({
        'websocket': AuthMiddlewareStack(
            SessionMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            ),
        ),
    })
    
    async def connect(user):
        client = APIClient()
        await sync_to_async(client.force_login)(user)

        communicator = WebsocketCommunicator(application, f'/ws/duel/{open_duel.id}/')
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        assert connected
        return communicator
    
    async def handle_message(communicator, message):
        await communicator.send_json_to(message)
        response = await communicator.receive_json_from()
        return response
    
    communicators = await asyncio.gather(connect(user1), connect(user2))
    
    for communicator in communicators:
        try:
            message = await asyncio.wait_for(communicator.receive_from(), timeout=5.0)
            print(message)
        except asyncio.TimeoutError:
            print("No message received in 5 seconds")

    await asyncio.gather(*[communicator.disconnect() for communicator in communicators])
    
    
    
