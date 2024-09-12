from django.db import models
from personality.models import Personal

class Message(models.Model):
    sender = models.ForeignKey(Personal, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Personal, related_name='received_messages', on_delete=models.CASCADE)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    media = models.FileField(upload_to='chats', null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content}'

class Visibility(models.Model):
    message = models.ForeignKey(Message, related_name='visibilities', on_delete=models.CASCADE)
    personal = models.ForeignKey(Personal, related_name='visibilities', on_delete=models.CASCADE)

    def __str__(self):
        return f'Visibility of {self.message} for {self.personal}'
