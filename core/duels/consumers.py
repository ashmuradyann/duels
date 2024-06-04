import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import StopConsumer
from asgiref.sync import sync_to_async
from .handlers import DuelHandler


class ConsumerBase(AsyncWebsocketConsumer):
    
    async def __disconnect__(self, close_code):
        await self.channel_layer.group_discard(
            self.groups['duel'],
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.groups['personal'],
            self.channel_name
        )
        await self.close(code=1000)
     
    async def connect(self):
        self.duel_id = self.scope['url_route']['kwargs']['duel_id']
        self.duel_handle = await sync_to_async(DuelHandler)(self.duel_id)            
        self.duel = self.duel_handle.duel
        self.user = self.scope['user']
        
        if not self.duel:
            await self.close(code=1000)
            raise StopConsumer()
        
        self.groups = {
            'duel': f'duel_{self.duel.id}',
            'part': f'duel_{self.duel.id}_',
            'personal': f'duel_{self.duel.id}_{self.user.id}'
        }
        
        await self.channel_layer.group_add(
            self.groups['duel'],
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.groups['personal'],
            self.channel_name
        )
        await self.accept()
        await self.check_player()
    
    async def check_player(self):
        self.players = await sync_to_async(self.duel_handle.get_players)({'1': None, '2': None})
        if self.players['1'] != self.user:
            approved = await sync_to_async(self.duel_handle.check_new_player)(self.user)
            if approved:
                await self.join_request()
            else:
                await self.__disconnect__(close_code=1000)

    async def refresh_signal(self, ignore=None, event=None):
        await self.channel_layer.group_send(
            self.groups['duel'],
            {
                'type': 'refresh_process',
                'ignore': ignore,
            }
        )
    
    async def refresh_process(self, event=None):
        if event.get('ignore') == None or self.user.id != event.get('ignore'):
            self.duel = await sync_to_async(self.duel_handle.get_duel_update)()
            self.players = await sync_to_async(self.duel_handle.get_players)(self.players)
   

class ConsumerSender(ConsumerBase):
    
    async def __send_event__(self, event, event_type):
        await self.send(text_data=json.dumps({**event, 'type': event_type})) 

    async def join_request_sender(self, event):
        await self.__send_event__(event, 'join_request')
          
    async def join_accepted_sender(self, event):
        await self.__send_event__(event, 'join_accepted')
        
    async def join_rejected_sender(self, event):
        await self.__send_event__(event, 'join_rejected')
        await self.__disconnect__(close_code=1000)
        
    async def duel_pending_sender(self, event):
        await self.__send_event__(event, 'duel_pending')  
    
    async def duel_started_sender(self, event):
        await self.__send_event__(event, 'duel_started')
    
    async def duel_winner_chosen_sender(self, event):
        await self.__send_event__(event, 'duel_winner_chosen')
        
    async def duel_canceled_sender(self, event):
        await self.__send_event__(event, 'duel_canceled')
    
    async def duel_contesting_sender(self, event):
        await self.__send_event__(event, 'duel_contesting')
    
    
class DuelConsumer(ConsumerSender):
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'join_accepted':
            await self.join_accepted(data)
        if data['type'] == 'join_rejected':
            await self.join_rejected(data)
        if data['type'] == 'ready_to_start':
            await self.ready_to_start()
        if data['type'] == 'leave_duel':
            await self.leave_duel(data)
        if data['type'] == 'i_won' or data['type'] == 'i_lost':
            await self.duel_completed(True if data['type'] == 'i_won' else False)
            
    async def join_request(self, event=None):
        group = self.groups['part'] + str(self.players['1'].id)
        await self.channel_layer.group_send(
            group,
            {
                'type': 'join_request_sender', 
                'message': f'{self.user.username} wants to join the duel',
                'duel_id': self.duel.id,
                'player_1_id': self.players['1'].id,
                'player_2_id': self.user.id,
                'player_1_username': self.players['1'].username,
                'player_2_username': self.user.username,
            }
        )

    async def join_rejected(self, event):
        await self.channel_layer.group_send(
            self.groups['part'] + str(event['player_2_id']),
            {
                'type': 'join_rejected_sender',
                'message': f'{self.user.username} rejected the join request',
                'duel_id': self.duel.id,
                'player_1_id': self.players['1'].id,
                'player_2_id': self.user.id,
                'player_1_username': self.players['1'].username,
                'player_2_username': self.user.username,
            }
        )

    async def join_accepted(self, event):
        await sync_to_async(self.duel_handle.set_player_2)(event.get('player_2_id'))
        self.players = await sync_to_async(self.duel_handle.get_players)(self.players)
        await self.refresh_signal()
        await self.channel_layer.group_send(
            self.groups['part'] + str(self.players['2'].id),
            {
                'type': 'join_accepted_sender',
                'message': f'{self.user.username} accepted the join request',
                'duel_id': self.duel.id,
                'player_1_id': self.players['1'].id,
                'player_2_id': self.players['2'].id,
                'player_1_username': self.players['1'].username,
                'player_2_username': self.players['2'].username,
            }
        )      

    async def ready_to_start(self, event=None):
        n = '1' if self.players['1'] == self.user else '2'
        await sync_to_async(lambda: setattr(self.duel, f'player_{n}_ready', True))()
        await sync_to_async(lambda: self.duel.save(update_fields=[f'player_{n}_ready']))()
        await self.refresh_signal(ignore=self.user.id)     
       
    async def duel_completed(self, i_won, event=None):
        await sync_to_async(self.duel_handle.set_win_status)(self.user, i_won)
        await self.refresh_signal()

        result = await sync_to_async(self.duel_handle.check_winner)()
        if result == 'completed':
            winner = await sync_to_async(lambda: self.duel.winner)()
            await self.duel_winner_chosen(winner)
        elif result == 'contesting':
            await self.duel_contesting()
            
    async def duel_winner_chosen(self, winner, event=None):
        await sync_to_async(self.duel_handle.set_status_completed)(winner)
        for player_id in [self.players['1'].id, self.players['2'].id]:
            await self.channel_layer.group_send(
                self.groups['part'] + str(player_id),
                {
                    'type': 'duel_winner_chosen_sender',
                    'message': f'{winner.username} is the winner!',
                    'duel_id': self.duel.id,
                    'winner_id': winner.id,
                    'winner_username': winner.username,
                    'player_1_id': self.players['1'].id,
                    'player_2_id': self.players['2'].id,
                    'player_1_username': self.players['1'].username,
                    'player_2_username': self.players['2'].username,
                }
            )

    async def duel_contesting(self, event=None):
        for player_id in [self.players['1'].id, self.players['2'].id]:
            await self.channel_layer.group_send(
                self.groups['part'] + str(player_id),
                {
                    'type': 'duel_contesting_sender',
                    'message': 'The duel is contested',
                    'duel_id': self.duel.id,
                    'player_1_id': self.players['1'].id,
                    'player_2_id': self.players['2'].id,
                    'player_1_username': self.players['1'].username,
                    'player_2_username': self.players['2'].username,
                }
            )

    async def leave_duel(self, event):
        leaver = self.user
        await sync_to_async(self.duel_handle.cancel_duel)(leaver)

