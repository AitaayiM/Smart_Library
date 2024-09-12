from django.test import TestCase
from identity.models import Profile, User, Role, Roles

class UserModelTestCase(TestCase):
    def test_create_user(self):
        # Créer les rôles
        guest_role = Role.objects.create(name=Roles.GUEST)
        # Créer un utilisateur
        user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='johndoe@example.com',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password'
        )
        # Ajouter le rôle guest à l'utilisateur
        user.roles.add(guest_role)
        # Vérifier que l'utilisateur est créé correctement
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.username, 'johndoe@example.com')
        self.assertEqual(user.date_of_birth, '1990-01-01')
        self.assertEqual(user.gender, 'Male')
        self.assertTrue(user.roles.filter(name=Roles.GUEST).exists())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        # Vérifier que le profil est créé pour cet utilisateur
        self.assertIsNotNone(user.profile)
        self.assertIsInstance(user.profile, Profile)

    def test_create_superuser(self):
        # Créer les rôles
        admin_role = Role.objects.create(name=Roles.ADMIN)
        # Créer un superutilisateur
        superuser = User.objects.create_superuser(
            first_name='Admin',
            last_name='User',
            username='admin@example.com',
            date_of_birth='1980-01-01',
            gender='Male',
            password='adminpassword'
        )
        # Ajouter le rôle admin à l'utilisateur
        superuser.roles.add(admin_role)
        # Vérifier que le superutilisateur est créé correctement
        self.assertEqual(superuser.first_name, 'Admin')
        self.assertEqual(superuser.last_name, 'User')
        self.assertEqual(superuser.username, 'admin@example.com')
        self.assertEqual(superuser.date_of_birth, '1980-01-01')
        self.assertEqual(superuser.gender, 'Male')
        self.assertTrue(superuser.roles.filter(name=Roles.ADMIN).exists())
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_admin)
        # Vérifier que le profil est créé pour le superutilisateur
        self.assertIsNotNone(superuser.profile)
        self.assertIsInstance(superuser.profile, Profile)
