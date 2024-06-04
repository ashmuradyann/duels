from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Duels
from .handlers import DuelHandler
from .tasks import complete_second_step_auto, complete_first_step_auto

@receiver(post_save, sender=Duels)
def update_ready_to_start(sender, instance, **kwargs):
    if instance.player_1_ready and instance.player_2_ready and instance.status == 'pending':
        handler = DuelHandler(instance.id)
        handler.set_status_started()

@receiver(pre_save, sender=Duels)
def duel_winner_changed(sender, instance, **kwargs):
    if instance.pk and instance.status == 'completed':
        original = sender.objects.get(pk=instance.pk)
        
        original_winner = original.winner
        new_winner = instance.winner

        if original.status == 'contesting' or 'completed':
            if not original_winner and new_winner:
                new_winner.balance += instance.bet * 2
                new_winner.save()
            elif original_winner and new_winner and new_winner != original_winner:
                new_winner.balance += instance.bet * 2
                new_winner.save()
                original_winner.balance -= instance.bet * 2
                original_winner.save()

@receiver(post_save, sender=Duels)
def duel_pending(sender, instance, **kwargs):
    if instance.status == 'pending':
        complete_first_step_auto.apply_async(args=[instance.id], countdown=120)

@receiver(post_save, sender=Duels)
def duel_started(sender, instance, **kwargs):
    if instance.status == 'started':
        complete_second_step_auto.apply_async(args=[instance.id], countdown=1800)
