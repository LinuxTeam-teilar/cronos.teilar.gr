'''
Needed by django-setuptest
'''
import os,sys
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from django.conf import settings

DATABASES = settings.DATABASES

#INSTALLED_APPS = ('tests_cronos')
#INSTALLED_APPS = settings.INSTALLED_APPS + ('tests_cronos',)
#print INSTALLED_APPS
