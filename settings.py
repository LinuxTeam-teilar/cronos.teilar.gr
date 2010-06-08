# -*- coding: utf-8 -*-

# Django settings for cronos project.

ADMINS = (
	('cephalon, tampakrap', 'cronos@cephalon.teilar.gr'),
)

SEND_BROKEN_LINK_EMAILS = False

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
LANGUAGE_CODE = 'el-gr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.load_template_source',
	'django.template.loaders.app_directories.load_template_source',
#	'django.template.loaders.eggs.load_template_source',
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
	'cronos.user',
)

AUTHENTICATION_BACKENDS = (
	'cronos.ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',
	'django.contrib.auth.backends.ModelBackend',
)

# Needed for the decorator
LOGIN_URL = '/'

# Needed for the custom user profile
AUTH_PROFILE_MODULE = 'user.LdapProfile'

# LDAP
LDAP_SERVER = 'localhost'
LDAP_PORT = 389
LDAP_URL = 'ldap://%s:%s' % (LDAP_SERVER, LDAP_PORT)
SEARCH_DN = 'ou=teilarStudents,dc=teilar,dc=gr'
SEARCH_FIELDS = ['*']

##### LOCAL_SETTINGS #######

### Debug variables are in local settings for easy switch / testing
# DEBUG = False
# TEMPLATE_DEBUG = DEBUG

### Database configurations
# DATABASE_ENGINE = '(db)'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# DATABASE_NAME = '(secret)'             # Or path to database file if using sqlite3.
# DATABASE_USER = '(secret)'             # Not used with sqlite3.
# DATABASE_PASSWORD = '(secret)'         # Not used with sqlite3.
# DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
# DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Make this unique, and don't share it with anybody.
# SECRET_KEY = '(secret)'

### Proj_root and media could be different in local systems
# PROJECT_ROOT = '/home/code/cronos'
# MEDIA_ROOT = PROJECT_ROOT + 'media/'
# MEDIA_URL = '/media/'
# ADMIN_MEDIA_PREFIX = '/admin_media/'

### Eclass username / password, for the cron jobs
# ECLASS_USER = '(secret)'
# ECLASS_PASSWORD = '(secret)'

### LDAP username / password
# BIND_USER = '(secret)'
# BIND_PASSWORD = '(secret)'
