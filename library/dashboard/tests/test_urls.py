from django.test import SimpleTestCase
from django.urls import reverse, resolve
from dashboard.views import (
    admin_dashboard_data, writer_dashboard_data, post_dashboard_data, friends_followers_dashboard_data,
    reaction_variation_data, followers_friends_variation_data, admin_variation_data
)

class DashboardTestUrls(SimpleTestCase):

    def test_admin_dashboard_data_url_resolves(self):
        url = reverse('admin_dashboard')
        self.assertEqual(resolve(url).func, admin_dashboard_data)

    def test_writer_dashboard_data_url_resolves(self):
        url = reverse('writer_dashboard')
        self.assertEqual(resolve(url).func, writer_dashboard_data)

    def test_post_dashboard_data_url_resolves(self):
        url = reverse('post_dashboard', args=['1'])
        self.assertEqual(resolve(url).func, post_dashboard_data)

    def test_friends_followers_dashboard_data_url_resolves(self):
        url = reverse('friends_followers_dashboard')
        self.assertEqual(resolve(url).func, friends_followers_dashboard_data)
    
    def test_reaction_variation_data_url_resolves(self):
        url = reverse('reaction_variation_dashboard')
        self.assertEqual(resolve(url).func, reaction_variation_data)
    
    def test_followers_friends_variation_data_url_resolves(self):
        url = reverse('followers_friends_variation_dashboard')
        self.assertEqual(resolve(url).func, followers_friends_variation_data)
    
    def test_admin_variation_data_url_resolves(self):
        url = reverse('admin_variation_dashboard')
        self.assertEqual(resolve(url).func, admin_variation_data)
