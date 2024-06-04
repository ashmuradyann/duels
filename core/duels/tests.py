from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from .models import Duels, Maps
from rest_framework.test import APIClient

from core.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.testing import WebsocketCommunicator
from asgiref.sync import sync_to_async



class OpenDuelsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.map = Maps.objects.create(name='Bridge', image='bridge.jpg')
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.duel1 = Duels.objects.create(status='open', bet=100, player_1=self.user, map_name=self.map)
        self.duel2 = Duels.objects.create(status='open', bet=200, player_1=self.user, map_name=self.map)
        self.duel3 = Duels.objects.create(status='open', bet=300, player_1=self.user, map_name=self.map)
        self.duel4 = Duels.objects.create(status='canceled', bet=400, player_1=self.user, map_name=self.map)

    def test_get_duels_with_no_params(self):
        response = self.client.get(reverse('open-duels'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_get_duels_with_min_bet(self):
        response = self.client.get(reverse('open-duels'), {'min_bet': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_duels_with_max_bet(self):
        response = self.client.get(reverse('open-duels'), {'max_bet': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_duels_with_sorting(self):
        response = self.client.get(reverse('open-duels'), {'sorting': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['bet'], 300)


class CompletedDuelsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.map = Maps.objects.create(name='Bridge', image='bridge.jpg')
        self.user_1 = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.user_2 = CustomUser.objects.create_user(username='testuser2', password='testpass', balance=1000)
        self.client.login(username='testuser', password='testpass')
        self.duel1 = Duels.objects.create(status='open', bet=100, player_1=self.user_1, player_2=self.user_2, map_name=self.map)
        self.duel2 = Duels.objects.create(status='open', bet=200, player_1=self.user_1, player_2=self.user_2, map_name=self.map)
        self.duel3 = Duels.objects.create(status='open', bet=300, player_1=self.user_1, player_2=self.user_2, map_name=self.map)
        self.duel4 = Duels.objects.create(status='completed', bet=400, player_1=self.user_1, player_2=self.user_2, map_name=self.map, winner=self.user_1)

    def test_get_completed_duels_count(self):
        response = self.client.get(reverse('completed-duels'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 1)
        
        
class AllDuelsByTokenTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.map = Maps.objects.create(name='Bridge', image='bridge.jpg')
        self.user1 = CustomUser.objects.create_user(username='testuser1', password='testpass', balance=1000)
        self.user2 = CustomUser.objects.create_user(username='testuser2', password='testpass', balance=1000)
        self.duel1 = Duels.objects.create(status='open', bet=100, player_1=self.user1, player_2=self.user2, map_name=self.map)
        self.duel2 = Duels.objects.create(status='open', bet=200, player_1=self.user2, player_2=self.user1, map_name=self.map)
        self.duel3 = Duels.objects.create(status='open', bet=300, player_1=self.user1, player_2=self.user2, map_name=self.map)
        self.duel4 = Duels.objects.create(status='canceled', bet=400, player_1=self.user2, player_2=self.user1, map_name=self.map)
        
    def test_get_all_duels_by_token(self):
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(reverse('all-duels'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.get(reverse('all-duels'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        
        
class CreateDuelTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username='testuser', password='testpass', balance=1000)
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.map = Maps.objects.create(name='Bridge', image='bridge_image.png')

    def test_create_duel(self):
        data = {
            'bet': 100,
            'map_name': self.map.name,
            'date': '2022-01-01',
            'time': '12:00',
            'time_zone': 'UTC',
        }
        response = self.client.post(reverse('create-duel'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Duel created successfully.')
        self.assertTrue(Duels.objects.filter(id=response.data['duel_id']).exists())
        
        
      
async def test_create_socket():
    user1 = await sync_to_async(CustomUser.objects.create)(username='test_user_1', password='password', balance=1000)
    user2 = await sync_to_async(CustomUser.objects.create)(username='test_user_2', password='password', balance=1000)
    map_object = await sync_to_async(Maps.objects.create)(name='Test Map', image='test_map.jpg')
    open_duel = await sync_to_async(Duels.objects.create)(status='open', bet=100, player_1=user1, map_name=map_object)
    client = APIClient()
    

    await sync_to_async(client.force_login)(user1)
    jwt_response = await sync_to_async(client.get)('/users/jwt/', {
        'username': user1.username,
        'password': 'password',
    })
    application = ProtocolTypeRouter({
        'websocket': AuthMiddlewareStack(
            SessionMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        ),
    })
    
    communicator = WebsocketCommunicator(application, f'/ws/duel/{open_duel.id}/')
    communicator.scope['user'] = user1
    connected, _ = await communicator.connect()
    assert connected
    
    await communicator.disconnect()
