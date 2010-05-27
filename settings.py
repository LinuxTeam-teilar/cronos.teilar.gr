# -*- coding: utf-8 -*-

# Django settings for cronos project.

ADMINS = (
    ('cephalon, tampakrap', 'cronos@cephalon.teilar.gr'),
)

MANAGERS = ADMINS

from local_settings import *

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Athens'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'cronos.urls'

import os.path
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
#	PROJECT_ROOT + 'templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'cronos.announcements',
	'cronos.ldap_groups',
	'cronos.profildap',
)

AUTHENTICATION_BACKENDS = (
#	'cronos.backends.ldapBackend.LDAPBackend',
#	'cronos.openldap.views.OpenLDAP',
	'cronos.ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',
	'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/'

AUTH_PROFILE_MODULE = 'profildap.LdapProfile'

# ldap
LDAP_SERVER = 'localhost'
# If using non-SSL use these
LDAP_PORT = 389
LDAP_URL = 'ldap://%s:%s' % (LDAP_SERVER, LDAP_PORT)
# If using SSL use these:
# LDAP_PORT = 636
# LDAP_URL = 'ldaps://%s:%s' % (LDAP_SERVER, LDAP_PORT)
SEARCH_DN = 'ou=teilarStudents,dc=teilar,dc=gr'
# NT4_DOMAIN is used with Active Directory only, comment out for eDirectory
NT4_DOMAIN = ''
# sAMAccountName is usd with Active Directory
SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName','memberOf', 'cn']
# Use the following for eDirectory
#SEARCH_FIELDS = ['mail', 'givenName', 'sn', 'groupMembership', 'cn']
#CERT_FILE = '/path/to/your/cert.txt'
# BIND_USER and BIND_PASSWORD are used if your LDAP requires
# authentication in order to search, leave blank for anonymous bind, e.g.:
# BIND_USER = ''
# BIND_PASSWORD = ''
BIND_USER = 'cn=Manager,dc=teilar,dc=gr'
BIND_PASSWORD = 'skata'
