from celery import shared_task
from search.documents.personalDocument import PersonalDocument
from .models import Personal

@shared_task
def index_personal_task(instance_id):
    try:
        instance = Personal.objects.get(id=instance_id)
        PersonalDocument().update(instance)
    except Personal.DoesNotExist:
        pass

@shared_task
def remove_personalfrom_index_task(instance_id):
    try:
        instance = Personal.objects.get(id=instance_id)
        PersonalDocument().delete(instance)
    except Personal.DoesNotExist:
        pass
