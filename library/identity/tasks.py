from celery import shared_task
from search.documents.userDocument import UserDocument
from .models import User

@shared_task
def index_user_task(instance_id):
    try:
        instance = User.objects.get(id=instance_id)
        UserDocument().update(instance)
    except User.DoesNotExist:
        pass

@shared_task
def remove_userfrom_index_task(instance_id):
    try:
        instance = User.objects.get(id=instance_id)
        UserDocument().delete(instance)
    except User.DoesNotExist:
        pass
