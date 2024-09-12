from django.test import SimpleTestCase
from django.urls import reverse, resolve
from chat.views import send_message, get_messages, reply_to_message, update_message, delete_message, get_queue_token


class ChatTestUrls(SimpleTestCase):

    def test_send_message_url_resolves(self):
        url = reverse('send')
        self.assertEqual(resolve(url).func, send_message)

    def test_get_messages_url_resolves(self):
        url = reverse('get', args=[1])
        self.assertEqual(resolve(url).func, get_messages)

    def test_reply_to_message_url_resolves(self):
        url = reverse('reply', args=[1])
        self.assertEqual(resolve(url).func, reply_to_message)

    def test_update_message_url_resolves(self):
        url = reverse('update', args=[1])
        self.assertEqual(resolve(url).func, update_message)

    def test_delete_message_url_resolves(self):
        url = reverse('delete', args=[1])
        self.assertEqual(resolve(url).func, delete_message)

    def test_get_queue_token_url_resolves(self):
        url = reverse('get_queue_token')
        self.assertEqual(resolve(url).func, get_queue_token)


