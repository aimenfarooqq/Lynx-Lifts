from django.urls import path
from . import views

urlpatterns = [
    path('', views.choose, name='choose'),
    path('home/', views.index, name='index'),
    path('choose/', views.choose, name='choose'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('post-trip/', views.user_post_trip, name='post_trip'),
    # Driver
    path('driver/register/', views.driver_register, name='driver_register'),
    path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/logout/', views.driver_logout, name='driver_logout'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/accept/<int:trip_id>/', views.accept_trip, name='accept_trip'),
    path('driver/post-trip/', views.driver_post_trip, name='driver_post_trip'),

    # Chat
    path('chat/<int:trip_id>/', views.chat, name='chat'),
    # Join Trip
    path('trip/join/<int:trip_id>/', views.join_trip, name='join_trip'),
    # Delete Trip - only for the user who posted it
    path('trip/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
]