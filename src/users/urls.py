from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views


app_name = 'users'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registration/', views.registration, name='registration'),
    re_path(r'^registration/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.registration_confirm, name='registration_confirm'),
    path('registration_confirm/', views.registration_confirm_repeat, name='registration_confirm_repeat'),

    path('password_reset/', views.password_reset, name='password_reset'),
    re_path(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),

    path('', views.profile, name='profile'),
]
