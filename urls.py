from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from cronos.accounts.views import about, index, preferences
from cronos.announcements.views import announcements
from cronos.announcements.feeds import AnnouncementFeed
from cronos.dionysos.views import dionysos
from cronos.eclass.views import eclass
from cronos.library.views import library
from cronos.login.views import cronos_login
from cronos.psigeia.views import psigeia
from cronos.teachers.views import teachers
from cronos.webmail.views import webmail


admin.autodiscover()

feeds = {
    'announcements': AnnouncementFeed,
}

handler500 = 'cronos.login.views.server_error'

urlpatterns = patterns('',
    (r'^$', index),
    (r'^about/', about),
    (r'^admin/', include(admin.site.urls)),
    (r'^announcements/', announcements),
    (r'^dionysos/', dionysos),
    (r'^eclass/', eclass),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^library/', library),
    (r'^login/', cronos_login),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login'}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
    (r'^preferences/', preferences),
    (r'^psigeia/', psigeia),
    (r'^teachers/', teachers),
    (r'^webmail/', webmail),
)
