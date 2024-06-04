from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chats, Messages
from asgiref.sync import sync_to_async
from .models import Duels
from .serializers import MessagesSerializer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.duel_id = self.scope['url_route']['kwargs']['duel_id']
        
        try:
            self.duel = await sync_to_async(Duels.objects.get)(id=self.duel_id)
        except Duels.DoesNotExist:
            await self.close(code=4000)
            return
        
        if not (self.user == self.duel.player_1 or self.user == self.duel.player_2 or self.user.staff):
            await self.close(code=4001)
            return
        
        await self.accept()

        group_name = f'chat_{self.duel.id}'
        await self.channel_layer.group_add(group_name, self.channel_name)

        self.chat, created = await sync_to_async(Chats.objects.get_or_create)(duel=self.duel, player=self.user)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'message':
            await self.send_message(data)
        elif message_type == 'get_messages':
            await self.get_messages()

    async def disconnect(self, close_code):
        group_name = f'chat_{self.duel.id}'
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def get_messages(self):
        messages = await sync_to_async(list)(Messages.objects.filter(chat=self.chat))
        await self.send(text_data=json.dumps({'messages': MessagesSerializer(messages, many=True).data}))

    async def send_message(self, event):
        message = await sync_to_async(Messages.objects.create)(chat=self.chat, user=self.user, message=event['message'])
        await self.channel_layer.group_send(
            f'chat_{self.duel.id}',
            {'type': 'chat_message', 'message': MessagesSerializer(message).data}
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
