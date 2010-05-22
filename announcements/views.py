# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

announce = []
i = 0

a = Announcements.objects.order_by('date_fetched')[:30]
print a[1]

for item in a:
	announce.append([])
	announce1 = [item.author(), str(item.date()), item.get_absolute_url(), item.__unicode__()]
	for j in xrange(4):
		announce[i].append(announce1[j][:])
	i += 1

def announcements(request):
	template = get_template('announcements.html')
	variables = Context({
		'announce': announce,
	})
	output = template.render(variables)
	return HttpResponse(output)
