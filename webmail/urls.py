from django.conf.urls.defaults import *

urlpatterns = patterns('cronos.webmail.views',
	url(r'^$','passed_id',name="passed_id"),
)
