"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  path('blog/', include(blog_urls))
"""
from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = 'squads'
urlpatterns = [
    path('', views.main, name='main'),
    path('registration/', views.registration, name='registration'),
    path('profile/', views.profile, name='profile'),
    path('leave/', views.leave, name='leave'),
    path('remove/', views.remove, name='remove'),
    path('join/<int:squad_id>/<str:code>/', views.join, name='join'),
]
