from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from .views import Activate

urlpatterns = [
    path('', views.home, name='home'),   
    
    path('room/<str:pk>/', views.room, name='room'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    
    # path('login/', LoginView.as_view(template_name="base/login_register.html"), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('changepassword/', views.changepwd, name='change-password'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.register, name='register'),
    path('update-user/', views.updateUser, name='update-user'),
    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),
    path('sendemail/', views.sendemail, name="sendemail"),
    path('change_password/<str:token>', views.Change_password, name="changepassword"),
    path('activate/<str:uidb64>/<str:token>/', views.Activate, name='activate'),
    path('resendmail/', views.ResendMail, name='resendmail'),
]