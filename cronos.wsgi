import os
import sys

os.eniron['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
