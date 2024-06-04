from celery import shared_task
from .handlers import DuelHandler

@shared_task
def complete_first_step_auto(duel_id):
    handler = DuelHandler(duel_id)
    handler.get_duel_update()
    not_ready = handler.get_not_ready()
    leaver = None
    if len(not_ready) > 0:
        if len(not_ready) == 1:
            leaver = not_ready[0]
        handler.set_status_canceled(leaver)
        
        
@shared_task
def complete_second_step_auto(duel_id):
    handler = DuelHandler(duel_id)
    handler.set_status_completed()
    duel = handler.get_duel_update()
    
    if duel.status == 'started' and not duel.player_1_is_winner and not duel.player_2_is_winner:
        handler.set_status_canceled()
    elif duel.status == 'started' and duel.player_1_is_winner or duel.player_2_is_winner:
        winner = duel.player_1 if duel.player_1_is_winner else duel.player_2
        handler.set_status_completed(winner)
    
    