from django.urls import path
from .views import admin_dashboard_data, writer_dashboard_data, post_dashboard_data, friends_followers_dashboard_data, reaction_variation_data, followers_friends_variation_data, admin_variation_data

urlpatterns = [
    path('admin', admin_dashboard_data, name='admin_dashboard'),
    path('writer', writer_dashboard_data, name='writer_dashboard'),
    path('post/<str:pk>', post_dashboard_data, name='post_dashboard'),
    path('friends_followers', friends_followers_dashboard_data, name='friends_followers_dashboard'),
    path('reaction_variation', reaction_variation_data, name='reaction_variation_dashboard'),
    path('followers_friends_variation', followers_friends_variation_data, name='followers_friends_variation_dashboard'),
    path('admin_variation', admin_variation_data, name='admin_variation_dashboard'),
]
