from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('send_code/', views.send_code, name='send_code'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('', views.sign_in, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/<str:referral_code>/', views.change_pass, name='change_password'),
    path('change_phone/<str:referral_code>/', views.change_phone, name='change_phone'),
    path('reset_password/', views.reset_password, name='reset_password' ),

] 