from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from identity.models import User, Role, Roles
from ebook.models import EBook
from rest_framework_simplejwt.tokens import AccessToken
from django.core.files.uploadedfile import SimpleUploadedFile

class EBookViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'password': 'password',
        }
        self.user = User.objects.create_user(**self.user_data)
        guest_role = Role.objects.create(name=Roles.GUEST)
        self.user.roles.add(guest_role)
        self.token = AccessToken.for_user(self.user)

        self.ebook_data = {
            'author': self.user,
            'title': 'Test Book',
            'summary': 'Test summary',
            'pages': '100',
            'category': 'Fiction',  
            'published_at':'2024-05-15',
            'content':SimpleUploadedFile('test_book.pdf', b'file_content')
        }
        self.ebook = EBook.objects.create(**self.ebook_data)

    def test_get_all_ebooks(self):
        url = reverse('ebook:ebooks')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_by_id_ebook(self):
        url = reverse('ebook:get_by_id_ebook', args=[self.ebook.pk])
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_ebook(self):
        url = reverse('ebook:delete_ebook', args=[self.ebook.pk])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)