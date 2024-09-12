from django.urls import path
from . import views


urlpatterns = [
    path('userinfo/', views.current_info,name='user_info'), 
    path('userinfo/update/', views.update_user,name='update_user'), 
    path('available/', views.available, name='available'),
    path('signup/', views.register, name='signup'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('login/', views.login, name='login'),
    path('verify/', views.login_verification, name='verify'),
    path('users/', views.get_all_users, name='users'),
    path('logout/', views.logout, name='logout'),
    path('users/<str:username>/delete/', views.delete_user, name='delete_user'),
]
