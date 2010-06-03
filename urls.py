# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from cronos.signup.forms import SignupCronos, SignupDionysos, SignupEclass, SignupWebmail
from cronos.signup.views import SignupWizard

from cronos.announcements.feeds import LatestEntries

from cronos.login.views import *
from cronos.eclass.views import *
#from cronos.dionysos.views import *
from cronos.webmail.views import *
from cronos.announcements.views import *
from cronos.user.views import *

admin.autodiscover()

feeds = {
	'announcements':LatestEntries,
	}

urlpatterns = patterns('',
	(r'^$', mylogin),
	(r'^eclass/', eclass),
#	(r'^dionysos', dionysos),
	(r'^webmail/', webmail),
	(r'^announcements/', announcements),
	(r'^logout/', mylogout),
	(r'^user/', user),

	url(r'^library/', include('cronos.library.urls')),

	url(r'^ldap/', include('cronos.ldap_groups.urls')),

	(r'^signup/', SignupWizard([SignupCronos, SignupDionysos, SignupEclass, SignupWebmail])),

	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
