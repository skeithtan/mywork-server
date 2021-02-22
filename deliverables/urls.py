from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('auth/sign-in/', views.sign_in_view),
    path('auth/sign-up/', views.create_profile_view),
    path('profile/', views.get_profile_view),
]
