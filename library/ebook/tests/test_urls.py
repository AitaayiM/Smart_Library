from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ebook.views import get_all_ebooks, get_by_id_ebook, add_ebook, update_ebook, delete_ebook, create_review, delete_review

class EbookTestUrls(SimpleTestCase):
    
    def test_get_all_ebooks_url_resolves(self):
        url = reverse('ebook:ebooks')
        self.assertEquals(resolve(url).func, get_all_ebooks)

    def test_get_by_id_ebook_url_resolves(self):
        url = reverse('ebook:get_by_id_ebook', args=['pk'])
        self.assertEquals(resolve(url).func, get_by_id_ebook)

    def test_add_ebook_url_resolves(self):
        url = reverse('ebook:add_ebook')
        self.assertEquals(resolve(url).func, add_ebook)

    def test_update_ebook_url_resolves(self):
        url = reverse('ebook:update_ebook', args=['pk'])
        self.assertEquals(resolve(url).func, update_ebook)

    def test_delete_ebook_url_resolves(self):
        url = reverse('ebook:delete_ebook', args=['1'])
        self.assertEquals(resolve(url).func, delete_ebook)

    def test_create_review_url_resolves(self):
        url = reverse('ebook:create_review', args=['pk'])
        self.assertEquals(resolve(url).func, create_review)

    def test_delete_review_url_resolves(self):
        url = reverse('ebook:delete_review', args=['pk'])
        self.assertEquals(resolve(url).func, delete_review)
