# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from cronos.announcements.feeds import *
from cronos.announcements.views import *
from cronos.dionysos.views import *
from cronos.eclass.views import *
from cronos.login.views import *
from cronos.recover.views import *
from cronos.signup.forms import *
from cronos.signup.views import *
from cronos.teachers.views import *
from cronos.user.views import *
from cronos.webmail.views import *

admin.autodiscover()

feeds = {
	'announcements': AnnouncementFeed,
	}

handler500 = 'cronos.login.views.server_error'

urlpatterns = patterns('',
	(r'^$', mylogin),
	(r'^eclass/', eclass),
	(r'^dionysos/', dionysos),
	(r'^webmail/', webmail),
	(r'^logout/', mylogout),
	(r'^user/', user),
	(r'^settings/', user_settings),
	(r'^teachers/', teachers),
	(r'^about/', about),
	(r'^recover/', recover),

	url(r'^library/', include('cronos.library.urls')),

	(r'^signup/', signup),

	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

	(r'^announcements/', announcements),
	
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
	
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
