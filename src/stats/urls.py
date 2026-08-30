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
from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views


app_name = 'stats'
urlpatterns = [
    path('pilots/', views.pilot_rankings, name='pilots'),
    path('squads/', views.squad_rankings, name='squads'),
    re_path(r'^sorties/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_sorties, name='pilot_sorties'),
    re_path(r'^vlifes/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_vlifes, name='pilot_vlifes'),
    re_path(r'^awards/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_awards, name='pilot_awards'),
    re_path(r'^killboard/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_killboard, name='pilot_killboard'),
    path('missions/', views.missions_list, name='missions_list'),

    re_path(r'^squad/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad, name='squad'),
    re_path(r'^pilots/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad_pilots, name='squad_pilots'),

    re_path(r'^pilot/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot, name='pilot'),
    path('sortie/<int:sortie_id>/', views.pilot_sortie, name='pilot_sortie'),
    path('sortie/log/<int:sortie_id>/', views.pilot_sortie_log, name='pilot_sortie_log'),
    path('mission/<int:mission_id>/', views.mission, name='mission'),
    path('vlife/<int:vlife_id>/', views.pilot_vlife, name='pilot_vlife'),

    path('overall/', views.overall, name='overall'),

    path('online/', views.online, name='online'),
    path('', views.main, name='main'),

    # нужно чтобы работали url без имени
    path('pilot/<int:profile_id>/', views.pilot),
    re_path(r'^sorties/(?P<profile_id>\d+)/$', views.pilot_sorties),
    re_path(r'^vlifes/(?P<profile_id>\d+)/$', views.pilot_vlifes),
]
