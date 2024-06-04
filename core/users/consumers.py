from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OnlineConsumer(AsyncWebsocketConsumer):
    online_users = 0

    async def connect(self):
        self.room_group_name = 'online_users'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        if self.scope["user"].is_authenticated:
            OnlineConsumer.online_users += 1
        await self.accept()
        await self.send_online_users()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            OnlineConsumer.online_users -= 1
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.send_online_users()

    async def send_online_users(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'users_online',
                'message': OnlineConsumer.online_users
            }
        )

    async def users_online(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'online': message
        }))
        