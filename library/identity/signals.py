from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, Profile
from .tasks import index_user_task, remove_userfrom_index_task

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        profile = Profile(user=user)
        profile.save()

@receiver(post_save, sender=User)
def index_user(sender, instance, **kwargs):
    index_user_task.delay(instance.id)

@receiver(post_delete, sender=User)
def remove_user_from_index(sender, instance, **kwargs):
    remove_userfrom_index_task.delay(instance.id)
