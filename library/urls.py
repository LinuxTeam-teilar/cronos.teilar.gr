# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('cronos.library.views',
    url(r'^$','library',name="search"),
)
