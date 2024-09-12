from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from ebook.models import EBook
from .models import Following, Friendship, Share, Post, Comment, Reaction, Personal, Like
from django.shortcuts import get_object_or_404
from .tasks import index_personal_task, remove_personalfrom_index_task

@receiver(post_save, sender=Friendship)
@receiver(post_delete, sender=Friendship)
@receiver(post_save, sender=Following)
@receiver(post_delete, sender=Following)
@receiver(post_save, sender=Share)
@receiver(post_delete, sender=Share)
@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
@receiver(post_delete, sender=Comment)
@receiver(post_delete, sender=Reaction)
def update_personal(sender, instance, **kwargs):
    try:
        if sender == Following:
            personal = instance.follower
        else:
            personal = instance.personal

        if personal and Personal.objects.filter(id=personal.id).exists():
            personal.friends = Friendship.objects.filter(personal=personal).count()
            personal.followers = Following.objects.filter(followed_personal=personal).count()
            personal.follow_ups = Share.objects.filter(personal=personal).count()
            personal.posts = Post.objects.filter(personal=personal).count()
            personal.save()
    except Personal.DoesNotExist:
        pass

@receiver(post_save, sender=EBook)
@receiver(post_delete, sender=EBook)
def update_writer(sender, instance, **kwargs):
    writer = instance.author
    if writer:
        personal = Personal.objects.filter(user=writer).first()
        if personal:
            books_count = EBook.objects.filter(author=writer).count()
            personal.books_published = books_count
            personal.save()


@receiver(post_save, sender=Reaction)
@receiver(post_delete, sender=Reaction)
@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
@receiver(post_save, sender=Share)
@receiver(post_delete, sender=Share)
def update_post(sender, instance, **kwargs):
    post = None
    if sender == Reaction:
        post = instance.post
    elif sender == Comment:
        post = instance.post
    elif sender == Share:
        post = instance.post

    if post:
        post.likes = Like.objects.filter(post=post).count()
        post.shares = Share.objects.filter(post=post).count()
        post.comments = Comment.objects.filter(post=post).count()
        post.save()

@receiver(post_save, sender=Personal)
def index_personal(sender, instance, **kwargs):
    index_personal_task.delay(instance.id)

@receiver(post_delete, sender=Personal)
def remove_personalfrom_index(sender, instance, **kwargs):
    remove_personalfrom_index_task.delay(instance.id)

""""@receiver(post_save, sender=Reaction)
@receiver(post_delete, sender=Reaction)
def update_comment(sender, instance, **kwargs):
    if instance.comment_id:
        comment_id = instance.comment_id
        comment = Comment.objects.filter(id=comment_id)
        if comment.exists():
            comment.likes = Like.objects.filter(comment__id=comment_id).count()
            comment.save()"""
