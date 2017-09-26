"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.views.generic import RedirectView

from . import views


app_name = 'stats'
urlpatterns = [
    url(r'^pilots/$', views.pilot_rankings, name='pilots'),
    url(r'^squads/$', views.squad_rankings, name='squads'),
    url(r'^sorties/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_sorties, name='pilot_sorties'),
    url(r'^awards/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_awards, name='pilot_awards'),
    url(r'^killboard/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_killboard, name='pilot_killboard'),
    url(r'^missions/$', views.missions_list, name='missions_list'),

    url(r'^squad/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad, name='squad'),
    url(r'^pilots/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad_pilots, name='squad_pilots'),

    url(r'^pilot/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot, name='pilot'),
    url(r'^sortie/(?P<sortie_id>\d+)/$', views.pilot_sortie, name='pilot_sortie'),
    url(r'^sortie/log/(?P<sortie_id>\d+)/$', views.pilot_sortie_log, name='pilot_sortie_log'),
    url(r'^mission/(?P<mission_id>\d+)/$', views.mission, name='mission'),

    url(r'^online/$', views.online, name='online'),
    url(r'^$', views.main, name='main'),

    # нужно чтобы работали url без имени
    url(r'^pilot/(?P<profile_id>\d+)/$', views.pilot),
    url(r'^sorties/(?P<profile_id>\d+)/$', views.pilot_sorties),
]
