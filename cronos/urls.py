# -*- coding: utf-8 -*-

#from cronos.announcements.feeds import AnnouncementsFeed
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#feeds = {
#    'announcements': AnnouncementsFeed,
#}

handler500 = 'cronos.common.views.server_error'

urlpatterns = patterns('',
    (r'^$', 'cronos.accounts.views.accounts_index'),
    (r'^about/', 'cronos.common.views.about'),
    (r'^announcements/', 'cronos.announcements.views.posts', {'title': u'Ανακοινώσεις', 'id': None}),
    (r'^departments/(\d+)/$', 'cronos.announcements.views.posts', {'title': u'Τμήμα'}),
    (r'^dionysos/', 'cronos.teilar.views.dionysos'),
    (r'^eclass/', 'cronos.teilar.views.eclass'),
#    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^library/', 'cronos.teilar.views.library'),
    (r'^login/', 'cronos.accounts.views.accounts_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^posts/(\d+)/$', 'cronos.announcements.views.posts', {'title': u'Άρθρο'}),
    (r'^refrigerators/', 'cronos.refrigerators.views.refrigerators'),
    (r'^settings/', 'cronos.accounts.views.settings'),
    (r'^teachers/$', 'cronos.teilar.views.teachers'),
    (r'^teachers/(\d+)/$', 'cronos.announcements.views.posts', {'title': u'Καθηγητής'}),
)

urlpatterns += staticfiles_urlpatterns()
