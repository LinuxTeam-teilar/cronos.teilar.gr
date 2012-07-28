# -*- coding: utf-8 -*-

#from apps.announcements.feeds import AnnouncementsFeed
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#feeds = {
#    'announcements': AnnouncementsFeed,
#}

handler500 = 'apps.login.views.server_error'

urlpatterns = patterns('',
    (r'^$', 'apps.accounts.views.index'),
    (r'^about/', 'apps.accounts.views.about'),
#    (r'^announcements/', 'apps.announcements.views.announcements'),
    (r'^dionysos/', 'apps.dionysos.views.dionysos'),
    (r'^eclass/', 'apps.eclass.views.eclass'),
#    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^library/', 'apps.library.views.library'),
    (r'^login/', 'apps.login.views.cronos_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^preferences/', 'apps.accounts.views.accounts_settings'),
    (r'^refrigerators/', 'apps.refrigerators.views.refrigerators'),
    (r'^teachers/', 'apps.teachers.views.teachers'),
)

urlpatterns += staticfiles_urlpatterns()
