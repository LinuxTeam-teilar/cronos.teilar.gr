from django.conf.urls.defaults import *

urlpatterns = patterns('cronos.library.views',
	url(r'^$','search',name="search"),
)
