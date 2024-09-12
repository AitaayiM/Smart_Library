from django.db import models
from django.utils.crypto import get_random_string
from identity.models import User

# Create your models here.
class Invitations(models.TextChoices):
    FRIENDSHIP = "Friendship"
    FOLLOWING = "Following"

class Replies(models.TextChoices):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class Reactions(models.TextChoices):
    LIKE = "Like"
    COMMENT = "Comment"
    SHARE = "Share"

class Personal(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    image = models.FileField(upload_to='images/personal/', blank=False)
    phone = models.CharField(max_length=20, blank=False)
    about_us = models.TextField(max_length=2000, default="", blank=False)
    country = models.TextField(max_length=50, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=False)
    verified = models.BooleanField(null=True, blank=False, default=False)
    bio = models.TextField(null=True, max_length=2000, blank=True)
    isbn = models.CharField(null=True, max_length=40, blank=False, unique=True)
    books_published = models.PositiveIntegerField(null=True, blank=True, default=0)
    posts = models.IntegerField(null=True, blank=False, default=0)
    friends = models.PositiveIntegerField(null=True, blank=False, default=0)
    followers = models.PositiveIntegerField(null=True, blank=False, default=0)
    follow_ups = models.PositiveIntegerField(null=True, blank=False, default=0)
    locked = models.BooleanField(null=True, blank=False, default=False)

    def get_absolute_url(self):
        return f"personal/{self.id}"
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Post(models.Model):
    personal = models.ForeignKey(Personal, null=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000, blank=False)
    image = models.FileField(upload_to='images/post/', null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=False)
    published_at = models.DateTimeField(null=True, blank=False)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)

class Comment(models.Model):
    personal = models.ForeignKey(Personal, null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, on_delete=models.CASCADE, related_name='comment')
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(max_length=2000, blank=False)
    image = models.FileField(upload_to='images/post/comment', null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=False)
    likes = models.PositiveIntegerField(default=0)

class Share(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='share')
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name='like')
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='like')
    created_at = models.DateTimeField(auto_now_add=True)

class Reaction(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    share = models.ForeignKey(Share, null=True, blank=True, on_delete=models.CASCADE)
    like = models.ForeignKey(Like, null=True, blank=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=8, null=True, choices=Reactions.choices)
    created_at = models.DateTimeField(auto_now_add=True)

class Invitation(models.Model):
    from_personal = models.ForeignKey(Personal, null=True, related_name='sent_invitations', on_delete=models.CASCADE)
    to_personal = models.ForeignKey(Personal, null=True, related_name='received_invitations', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, null=True, choices=Invitations.choices)
    status = models.CharField(max_length=10, null=True, choices=Replies.choices, default=Replies.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class Friendship(models.Model):
    personal = models.ForeignKey(Personal, null=True, on_delete=models.CASCADE, related_name='personal')
    friend = models.ForeignKey(Personal, null=True, on_delete=models.CASCADE, related_name='friend')
    queue_token = models.CharField(max_length=40, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Following(models.Model):
    follower = models.ForeignKey(Personal, null=True, related_name='following_relations', on_delete=models.CASCADE)
    followed_personal = models.ForeignKey(Personal, null=True, related_name='followers_relations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
