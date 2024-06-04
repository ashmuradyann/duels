from .models import Duels
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from users.models import CustomUser

class DuelHandler:
    def __init__(self, duel_id=None):
        self.duel_id = duel_id
        self.duel = Duels.objects.filter(id=duel_id).first() if duel_id else None
        self.players = self.get_players() if self.duel else None
        
    def check_new_player(self, user) -> bool:
        if self.duel.player_2 is None and user.balance >= self.duel.bet and user.leaves < 3:
            return True
        elif self.duel.player_2 == user or self.duel.player_1 == user:
            return True
        else:
            return False

    def check_winner(self) -> str:
        result = None
        if self.duel.player_1_is_winner == None or self.duel.player_2_is_winner == None:
            result = 'waiting'        
        elif self.duel.player_1_is_winner == True and self.duel.player_2_is_winner == True:
            result = 'contesting'
        elif self.duel.player_1_is_winner == False and self.duel.player_2_is_winner == False:
            result = 'contesting'
        elif self.duel.player_1_is_winner == True and self.duel.player_2_is_winner == False:
            result = 'completed'
            self.duel.winner = self.duel.player_1
        elif self.duel.player_2_is_winner == True and self.duel.player_1_is_winner == False:
            result = 'completed'
            self.duel.winner = self.duel.player_2 
        return result

    def get_duel_update(self):
        self.duel.refresh_from_db()
        return self.duel
    
    def get_players(self, players={'1': None, '2': None}):
        if self.duel:
            if not players['1']:
                players['1'] = self.duel.player_1 or None
            if not players['2']:
                players['2'] = self.duel.player_2 or None
        return players

    def get_not_ready(self):
        not_ready = []
        if not self.duel.player_1_ready:
            not_ready.append(self.duel.player_1)
        if not self.duel.player_2_ready:
            not_ready.append(self.duel.player_2)
        return not_ready
     
    def set_player_2(self, player_2_id):
        try:
            with transaction.atomic():
                player_2 = CustomUser.objects.get(id=player_2_id)
                player_2.balance = F('balance') - self.duel.bet
                player_2.save(update_fields=['balance'])
                self.set_status_pending(player_2)
        except CustomUser.DoesNotExist:
            raise ValueError("Player not found")
    
    def set_status_pending(self, player_2):
        with transaction.atomic():
            self.duel.player_2 = player_2
            self.duel.player_2_bet = self.duel.bet
            self.duel.status = 'pending'
            self.duel.pending_at = timezone.now()
            self.duel.save()
            
    def set_status_started(self):
        self.duel.status = 'started'
        self.duel.started_at = timezone.now()
        self.duel.save()
    
    def set_status_canceled(self, leaver=None):
        if self.duel.player_1_bet > 0:
            self.duel.player_1.balance += self.duel.player_1_bet
            self.duel.player_1_bet = 0
            self.duel.player_1.save()
        if self.duel.player_2_bet > 0:
            self.duel.player_2.balance += self.duel.player_2_bet
            self.duel.player_2_bet = 0
            self.duel.player_2.save()
        if self.duel.status in ['pending', 'started'] and leaver:
            if self.duel.player_1 == leaver:
                self.duel.player_1.leaves += 1
            elif self.duel.player_2 == leaver:
                self.duel.player_2.leaves += 1
            leaver.save()
        self.duel.status = 'canceled'
        self.duel.save()
    
    def set_status_completed(self, winner):
        with transaction.atomic():
            self.duel.winner = winner
            self.duel.status = 'completed'
            self.duel.completed_at = timezone.now()
            self.duel.player_1_bet = 0
            self.duel.player_2_bet = 0
            self.duel.save()
            
            winner.balance += self.duel.bet * 2
            winner.save()
        
    def set_win_status(self, user, i_won):
        if self.duel.player_1 == user:
            self.duel.player_1_is_winner = i_won
        elif self.duel.player_2 == user:
            self.duel.player_2_is_winner = i_won
        self.duel.save()
