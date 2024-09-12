from django.test import SimpleTestCase
from django.urls import reverse, resolve
from identity.views import update_user, available, register, login, login_verification, current_info, forgot_password, reset_password, get_all_users

class IdentityTestUrls(SimpleTestCase):
    
    def test_update_user_url_resolves(self):
        url = reverse('update_user')
        self.assertEquals(resolve(url).func, update_user)

    def test_current_info_url_resolves(self):
        url = reverse('user_info')
        self.assertEquals(resolve(url).func, current_info)

    def test_available_url_resolves(self):
        url = reverse('available')
        self.assertEquals(resolve(url).func, available)

    def test_register_url_resolves(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, register)

    def test_forgot_password_url_resolves(self):
        url = reverse('forgot_password')
        self.assertEquals(resolve(url).func, forgot_password)

    def test_reset_password_url_resolves(self):
        url = reverse('reset_password', args=['token'])
        self.assertEquals(resolve(url).func, reset_password)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login)

    def test_login_verification_url_resolves(self):
        url = reverse('verify')
        self.assertEquals(resolve(url).func, login_verification)

    def test_get_all_users_url_resolves(self):
        url = reverse('users')
        self.assertEquals(resolve(url).func, get_all_users)