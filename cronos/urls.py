# -*- coding: utf-8 -*-

from cronos.accounts.resources import UserResource
from cronos.posts.feeds import PostsFeed
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from tastypie.api import Api

handler500 = 'cronos.common.views.server_error'

urlpatterns = patterns('',
    (r'^$', 'cronos.accounts.views.accounts_index'),
    (r'^about/', 'cronos.common.views.about'),
    (r'^announcements/$', 'cronos.posts.views.posts', {'page': u'announcements', 'id': None}),
    (r'^api/', include(UserResource().urls)),
    (r'^blog/$', 'cronos.posts.views.posts', {'page': u'blog', 'id': None}),
    (r'^blog/feed/$', PostsFeed(), {'page': u'blog', 'username': None}),
    (r'^departments/(\d+)/$', 'cronos.posts.views.posts', {'page': u'department'}),
    (r'^dionysos/', 'cronos.teilar.views.dionysos'),
    (r'^eclass/', 'cronos.teilar.views.eclass'),
    (r'^announcements/(?P<username>\w+)/feed/$', PostsFeed(), {'page': u'announcements'}),
    (r'^library/', 'cronos.teilar.views.library'),
    (r'^login/', 'cronos.accounts.views.accounts_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^posts/(\d+)/$', 'cronos.posts.views.posts', {'page': u'post'}),
    (r'^refrigerators/', 'cronos.refrigerators.views.refrigerators'),
    (r'^settings/accounts/$', 'cronos.accounts.views.settings_accounts'),
    (r'^settings/announcements/$', 'cronos.accounts.views.settings_announcements'),
    (r'^teachers/$', 'cronos.teilar.views.teachers'),
    (r'^teachers/(\d+)/$', 'cronos.posts.views.posts', {'page': u'teacher'}),
)

urlpatterns += staticfiles_urlpatterns()
