from django.test import SimpleTestCase
from django.urls import reverse, resolve
from search.views import search_ebooks, search_users

class SearchTestUrls(SimpleTestCase):
    
    def test_search_ebooks_url_resolves(self):
        url = reverse('search_ebooks')
        self.assertEquals(resolve(url).func, search_ebooks)

    def test_search_users_url_resolves(self):
        url = reverse('search_users')
        self.assertEquals(resolve(url).func, search_users)