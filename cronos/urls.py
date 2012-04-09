# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from cronos.announcements.feeds import AnnouncementsFeed

admin.autodiscover()

feeds = {
    'announcements': AnnouncementsFeed,
}

handler500 = 'cronos.login.views.server_error'

urlpatterns = patterns('',
    (r'^$', 'cronos.accounts.views.index'),
    (r'^about/', 'cronos.accounts.views.about'),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^announcements/', 'cronos.announcements.views.announcements'),
    (r'^dionysos/', 'cronos.dionysos.views.dionysos'),
    (r'^eclass/', 'cronos.eclass.views.eclass'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^library/', 'cronos.library.views.library'),
    (r'^login/', 'cronos.login.views.cronos_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^preferences/', 'cronos.accounts.views.accounts_settings'),
    (r'^psigeia/', 'cronos.psigeia.views.psigeia'),
    (r'^teachers/', 'cronos.teachers.views.teachers'),
    (r'^webmail/', 'cronos.webmail.views.webmail'),
)

urlpatterns += staticfiles_urlpatterns()
