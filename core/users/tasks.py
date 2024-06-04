from celery import shared_task
from .models import CustomUser

@shared_task
def reset_leaves():
    CustomUser.objects.all().update(leaves=0)
    


