from django.db import models
from duels.models import Duels
from users.models import CustomUser

class Chats(models.Model):
    duel = models.ForeignKey(Duels, on_delete=models.CASCADE, limit_choices_to={'status': 'contesting'}, verbose_name='Duel')
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='User 1', related_name='chats_as_user_1')
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='User 2', related_name='chats_as_user_2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats'
        ordering = ['created_at']
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
    
    def __str__(self):
        return f'{self.user.username} - {self.message[:20]}'

class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f'{self.user.username} - {self.message[:20]}'
    