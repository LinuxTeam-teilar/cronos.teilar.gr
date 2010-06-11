# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from cronos.announcements.feeds import *
from cronos.announcements.views import *
from cronos.declaration.views import *
from cronos.eclass.views import *
from cronos.login.views import *
from cronos.signup.forms import SignupCronos, SignupDionysos, SignupEclass, SignupWebmail
from cronos.signup.views import SignupWizard
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
	(r'^declaration', declaration),
	(r'^webmail/', webmail),
	(r'^logout/', mylogout),
	(r'^user/', user),
	(r'^settings/', user_settings),

	url(r'^library/', include('cronos.library.urls')),

	url(r'^ldap/', include('cronos.ldap_groups.urls')),

	(r'^signup/', SignupWizard([SignupCronos, SignupDionysos, SignupEclass, SignupWebmail])),

	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

	(r'^announcements/', announcements),
	
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
	
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
