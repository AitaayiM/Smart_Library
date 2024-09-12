from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from personality.models import Personal
from chat.models import Message, Visibility

User = get_user_model()

class ChatModelTests(TestCase):

    def setUp(self):
        # Create User instances
        self.user1 = User.objects.create_user(
            username='user1@example.com',
            first_name='User',
            last_name='One',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2@example.com',
            first_name='User',
            last_name='Two',
            date_of_birth='1992-02-02',
            gender='Female',
            password='password123'
        )

        # Create Personal instances
        self.sender = Personal.objects.create(
            user=self.user1,
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            phone='1234567890',
            about_us='About sender',
            country='Country1',
            isbn='1234567890123'
        )
        self.receiver = Personal.objects.create(
            user=self.user2,
            image=SimpleUploadedFile(name='test_image2.jpg', content=b'', content_type='image/jpeg'),
            phone='0987654321',
            about_us='About receiver',
            country='Country2',
            isbn='1234567890124'
        )

        # Create Message instance
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello',
            media=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

        # Create Visibility instance
        self.visibility = Visibility.objects.create(
            message=self.message,
            personal=self.receiver
        )

    def test_message_creation(self):
        self.assertEqual(str(self.message), f'{self.sender} to {self.receiver}: Hello')
        self.assertEqual(self.message.sender, self.sender)
        self.assertEqual(self.message.receiver, self.receiver)
        self.assertEqual(self.message.content, 'Hello')
        self.assertIsNotNone(self.message.media)
        self.assertIsNotNone(self.message.timestamp)

    def test_visibility_creation(self):
        self.assertEqual(str(self.visibility), f'Visibility of {self.message} for {self.receiver}')
        self.assertEqual(self.visibility.message, self.message)
        self.assertEqual(self.visibility.personal, self.receiver)

    def test_message_parent(self):
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Parent Message',
            media=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )
        child_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Child Message',
            parent_message=parent_message,
            media=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )
        self.assertEqual(child_message.parent_message, parent_message)
        self.assertEqual(child_message.parent_message.content, 'Parent Message')

    def test_message_visibility(self):
        new_visibility = Visibility.objects.create(
            message=self.message,
            personal=self.sender
        )
        self.assertEqual(new_visibility.message, self.message)
        self.assertEqual(new_visibility.personal, self.sender)
