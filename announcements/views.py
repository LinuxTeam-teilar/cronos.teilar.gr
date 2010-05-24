# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

announce = []
i = 0

a = Announcements.objects.order_by('-date_fetched')[:30]

for item in a:
	announce.append([])
	if (item.urlid.urlid[:2] == 'CS'):
		img = 'eclass'
	else:
		img = item.urlid.urlid
	announce1 = [img, item.author(), str(item.date()), item.get_absolute_url(), item.__unicode__(), item.body()]
	for j in xrange(5):
		announce[i].append(announce1[j][:])
	i += 1

def announcements(request):
	template = get_template('announcements.html')
	variables = Context({
		'items': announce,
		'MEDIA_URL': settings.MEDIA_URL,
	})
	output = template.render(variables)
	return HttpResponse(output)
