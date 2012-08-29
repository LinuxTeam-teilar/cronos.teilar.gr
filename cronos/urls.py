# -*- coding: utf-8 -*-

#from cronos.announcements.feeds import AnnouncementsFeed
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#feeds = {
#    'announcements': AnnouncementsFeed,
#}

handler500 = 'cronos.accounts.views.server_error'

urlpatterns = patterns('',
    (r'^$', 'cronos.accounts.views.accounts_index'),
    (r'^about/', 'cronos.accounts.views.about'),
#    (r'^announcements/', 'cronos.announcements.views.announcements'),
    (r'^dionysos/', 'cronos.dionysos.views.dionysos'),
    (r'^eclass/', 'cronos.eclass.views.eclass'),
#    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^library/', 'cronos.teilar.views.library'),
    (r'^login/', 'cronos.login.views.cronos_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^preferences/', 'cronos.accounts.views.accounts_settings'),
    (r'^refrigerators/', 'cronos.refrigerators.views.refrigerators'),
    (r'^teachers/', 'cronos.teilar.views.teachers'),
)

urlpatterns += staticfiles_urlpatterns()
