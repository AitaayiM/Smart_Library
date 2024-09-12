from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EBook, Review
from .tasks import index_ebook_task, remove_ebookfrom_index_task

@receiver(post_save, sender=EBook)
def index_ebook(sender, instance, **kwargs):
    index_ebook_task.delay(instance.id)

@receiver(post_delete, sender=EBook)
def remove_ebook_from_index(sender, instance, **kwargs):
    remove_ebookfrom_index_task.delay(instance.id)

@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_ebook_reviews(sender, instance, **kwargs):
    ebook = instance.ebook
    if ebook:
        review_count = Review.objects.filter(ebook=ebook).count()
        ebook.review_count = review_count
        ebook.save()
