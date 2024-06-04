from django.db import models

class Duels(models.Model):
    status_choices = (
        ('open', 'Open'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('contesting', 'Contesting')
    )
    
    map_name = models.ForeignKey('Maps', on_delete=models.PROTECT)
    bet = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    time_zone = models.CharField(max_length=100, blank=True, null=True)
    
    player_1 = models.ForeignKey('users.CustomUser', related_name='player_1', on_delete=models.PROTECT, blank=True, null=True)
    player_2 = models.ForeignKey('users.CustomUser', related_name='player_2', on_delete=models.PROTECT, blank=True, null=True)
    
    player_1_ready = models.BooleanField(default=False)
    player_2_ready = models.BooleanField(default=False)
    
    player_1_is_winner = models.BooleanField(null=True, blank=True)
    player_2_is_winner = models.BooleanField(null=True, blank=True)
    
    player_1_bet = models.PositiveIntegerField(default=0)
    player_2_bet = models.PositiveIntegerField(default=0)

    winner = models.ForeignKey('users.CustomUser', related_name='winner', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(max_length=10, choices=status_choices, default='open')
    
    created_at = models.DateTimeField(auto_now_add=True)
    pending_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Duel'
        verbose_name_plural = 'Duels'
        

class Maps(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.URLField()
    
    class Meta:
        verbose_name = 'Map'
        verbose_name_plural = 'Maps'
    
    def __str__(self):
        return self.name