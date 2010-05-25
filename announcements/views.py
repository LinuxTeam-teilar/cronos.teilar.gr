# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from cronos.announcements.forms import AnnouncementForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

announce = []
i = 0

for item in Announcements.objects.order_by('-date_fetched')[:30]:
	announce.append([])
	if (item.urlid.urlid[:2] == 'CS'):
		img = 'eclass'
	else:
		img = item.urlid.urlid
	announce1 = [img, item.author(), str(item.date()), str(item.id), item.__unicode__()]
	for j in xrange(5):
		announce[i].append(announce1[j][:])
	i += 1

@login_required(redirect_field_name='/')
def announcements(request):
	form = AnnouncementForm(request.GET)
	if (len(str(request.GET.get('announceid'))) != 4):
		db = Announcements.objects.filter(id__exact = request.GET.get('announceid'))
		for item in db:		
			if (item.urlid.urlid[:2] == 'CS'):
				img = 'eclass'
			else:
				img = item.urlid.urlid
			announce2 = [img, item.author(), str(item.date()), item.__unicode__(), item.get_absolute_url(), item.body()]
		template = get_template('announcements.html')
		variables = Context({
			'id': 'set',
			'content': announce2,
		})
		output = template.render(variables)
		return HttpResponse(output)
	else:
		template = get_template('announcements.html')
		variables = Context({
			'items': announce,
			'MEDIA_URL': settings.MEDIA_URL,
		})
		output = template.render(variables)
		return HttpResponse(output)
	return render_to_response('announcements.html', {'form': form } )
