from django.urls import reverse
from rest_framework import status
from identity.models import User, Role, Roles
from ebook.models import EBook
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase, Client

class SearchViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        quest_role = Role.objects.create(name=Roles.GUEST)
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'password': 'password',
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.roles.add(quest_role)

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

    def test_search_users(self):
        response = self.client.get(reverse('search_users'), {'keyword': self.user_data['first_name']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['users'][0]['first_name'], self.user_data['first_name'])
    
    def test_search_ebooks(self):
        response = self.client.get(reverse('search_ebooks'), {'keyword': self.ebook_data['title']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['ebooks'][0]['title'], self.ebook_data['title'])
