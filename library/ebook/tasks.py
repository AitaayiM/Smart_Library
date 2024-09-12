from celery import shared_task
from search.documents.ebookDocument import EbookDocument
from .models import EBook

@shared_task
def index_ebook_task(instance_id):
    try:
        instance = EBook.objects.get(id=instance_id)
        EbookDocument().update(instance)
    except EBook.DoesNotExist:
        pass

@shared_task
def remove_ebookfrom_index_task(instance_id):
    try:
        instance = EBook.objects.get(id=instance_id)
        EbookDocument().delete(instance)
    except EBook.DoesNotExist:
        pass
