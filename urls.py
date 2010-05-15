# -*- coding: utf-8 -*-
#test
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from cronos.announcements.feeds import LatestEntries

#from cronos.main.views import *
#from cronos.all.views import *
#from cronos.eclass.views import *
from cronos.thesis.library.views import *
from cronos.dionysos.views import *
from cronos.webmail.views import *
#from cronos.sidebar.views import *
from cronos.announcements.views import *

admin.autodiscover()

feeds = {
	'latest':LatestEntries,
	}

urlpatterns = patterns('',
#	(r'^$', main),
#	(r'^all', all),
#    (r'^eclass', eclass),
#	(r'^library', ),
	(r'^dionysos', dionysos),
#	(r'^webmail/', webmail),
#	(r'^sidebar', sidebar),
	(r'^announcements', announcements),

	url(r'^library/', include('cronos.library.urls')),
	url(r'^webmail/', include('cronos.webmail.urls')),
#	url(r'^webmail/mail/','passed_id',name="passed_id")

	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
