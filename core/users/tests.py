from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from users.consumers import OnlineConsumer
import pytest
import json


class UserInfoTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_get_user_info_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(reverse('user_info'), {'pk': self.user.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, CustomUserSerializer(self.user).data)

    def test_get_user_info_unauthenticated(self):
        response = self.client.get(reverse('user_info'), {'pk': self.user.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "No pk provided"})
     
     
@pytest.mark.asyncio
async def test_online_consumer():
    application = AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/online/$', OnlineConsumer.as_asgi()),
        ])
    )
    communicator = WebsocketCommunicator(application, 'ws/online/')
    connected, _ = await communicator.connect()
    assert connected is True

    # Test sending text
    await communicator.send_to(text_data=json.dumps({'type': 'users_online', 'message': 1}))
    response = await communicator.receive_from()
    assert response == json.dumps({'online': 1})

    # Test disconnecting
    await communicator.disconnect()