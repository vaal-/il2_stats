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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView, TemplateView

import chunks.views
import users.views


urlpatterns = i18n_patterns(
    url(r'^profile/', include('users.urls', namespace='users')),
    url(r'^squad/', include('squads.urls', namespace='squads')),

    url(r'^robots\.txt$', RedirectView.as_view(url=staticfiles_storage.url('robots.txt'))),

    url(r'^admin/', admin.site.urls),
    url(r'^faq/$', chunks.views.page, {'key': 'faq', 'template': 'faq.html'}, name='faq'),
    url(r'^info/$', chunks.views.page, {'key': 'info', 'template': 'info.html'}, name='info'),
    url(r'^', include('stats.urls', namespace='stats')),
)


if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

    import debug_toolbar
    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])

    from django.views.defaults import server_error, page_not_found, permission_denied
    urlpatterns.extend([
        url(r'^403/$', permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', server_error),
    ])
