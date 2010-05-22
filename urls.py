# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from cronos.announcements.feeds import LatestEntries

#from cronos.main.views import *
#from cronos.frames.views import *
#from cronos.sidebar.views import *
#from cronos.eclass.views import *
#from cronos.dionysos.views import *
from cronos.webmail.views import *
#from cronos.announcements.views import *

admin.autodiscover()

feeds = {
	'announcements':LatestEntries,
	}

urlpatterns = patterns('',
#	(r'^$', frames),
#	(r'^main', main),
#	(r'^sidebar', sidebar),
#	(r'^eclass', eclass),
#	(r'^dionysos', dionysos),
	(r'^webmail/', webmail),
#	(r'^announcements', announcements),

	url(r'^library/', include('cronos.library.urls')),

	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
