from django.urls import path
from search.views import search_ebooks, search_users, search_personals

urlpatterns = [
    path("ebook/", search_ebooks, name='search_ebooks'),
    path("user/", search_users, name='search_users'),
    path("personal/", search_personals, name='search_personals'),
] 
