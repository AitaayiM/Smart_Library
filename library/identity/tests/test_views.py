from django.urls import reverse
from rest_framework import status
from identity.models import User, Role, Roles

from django.test import TestCase, Client
from rest_framework_simplejwt.tokens import AccessToken

class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        admin_role = Role.objects.create(name=Roles.ADMIN)
        # Créer un utilisateur pour les tests
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe@example.com',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'password': 'password',
        }
        # Créer un utilisateur en utilisant votre méthode de création d'utilisateur
        self.user = User.objects.create_user(**self.user_data)
        self.user.roles.add(admin_role)
        # Obtenir le jeton d'authentification pour cet utilisateur
        self.token = AccessToken.for_user(self.user)

    def test_current_info(self):
        # Faites une requête à la vue current_info en incluant le jeton d'authentification dans l'en-tête Authorization
        response = self.client.get(reverse('user_info'), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        # Vérifiez si la réponse est OK (200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available(self):
        # Faites une requête à la vue available
        response = self.client.get(reverse('available'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith@example.com',
            'password': 'password',
            'date_of_birth': '1995-01-01',
            'gender': 'Female'
        }
        response = self.client.post(reverse('signup'), data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 

    def test_forgot_password(self):
        data = {'email': 'johndoe@example.com'}
        response = self.client.post(reverse('forgot_password'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_users(self):
        response = self.client.get(reverse('users'), HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
