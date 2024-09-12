from django.urls import path
from .views import get_messages, send_message, reply_to_message, update_message, delete_message, get_queue_token

urlpatterns = [
    path('message/get/<int:friend_id>/', get_messages, name='get'),
    path('message/reply/<int:message_id>', reply_to_message, name='reply'),
    path('message/update/<int:message_id>', update_message, name='update'),
    path('message/delete/<int:message_id>/', delete_message, name='delete'),
    path('message/send', send_message, name='send'),
    path('message/token', get_queue_token, name='get_queue_token'),
]
