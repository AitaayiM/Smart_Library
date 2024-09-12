from django.urls import path
from . import views

app_name = 'ebook'

urlpatterns = [
    path('ebooks/', views.get_all_ebooks,name='ebooks'),
    path('ebooks/<str:pk>', views.get_by_id_ebook,name='get_by_id_ebook'),
    path('ebooks/add/', views.add_ebook,name='add_ebook'),
    path('ebooks/update/<str:pk>', views.update_ebook,name='update_ebook'),
    path('ebooks/delete/<str:pk>', views.delete_ebook,name='delete_ebook'),

    path('<str:pk>/reviews', views.create_review,name='create_review'),
    path('<str:pk>/reviews/delete', views.delete_review,name='delete_review'),
    
]