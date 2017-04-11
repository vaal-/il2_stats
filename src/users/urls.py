from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views


app_name = 'users'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^registration/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.registration_confirm, name='registration_confirm'),
    url(r'^registration_confirm/$', views.registration_confirm_repeat, name='registration_confirm_repeat'),

    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),

    url(r'^$', views.profile, name='profile'),
]
