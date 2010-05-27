from django.conf.urls.defaults import *
from ldap_groups.views import ldap_search

urlpatterns = patterns('',
    url(r'^ldap_search/$', ldap_search, name='ldap_search'),
)
