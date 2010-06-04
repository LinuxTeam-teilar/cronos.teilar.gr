# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from cronos.announcements.forms import AnnouncementForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

@login_required
def announcements(request):
	id = ''
	if (request.GET.get('announceid')):
		form = AnnouncementForm(request.GET)
		db = Announcements.objects.filter(id__exact = request.GET.get('announceid'))
		for item in db:
			announce = [item.author(), str(item.date()), item.__unicode__(), item.get_absolute_url(), item.body()]
		id = request.GET.get('announceid')
	else:
		form = AnnouncementForm()
		announce = []
		i = 0
		for item in Announcements.objects.order_by('-date_fetched'):
			if request.user.get_profile().school == item.urlid.urlid or item.urlid.urlid == 'cid52' or item.urlid.urlid == 'cid55' or item.urlid.urlid == 'cid51': #got to finish it
				img = item.urlid.urlid
				if (item.urlid.urlid[:2] == 'CS'):
					img = 'eclass'
				if (item.urlid.urlid[:3] == 'pid'):
					img = 'teacher'
				if (item.urlid.urlid == 'pid323') or (item.urlid.urlid == 'pid324'):
					img = item.urlid.urlid
				if (item.urlid.urlid == 'pid326') or (item.urlid.urlid == 'pid327'):
					img == 'meeting'
				if (item.urlid.urlid[:3] == 'cid') and (int(item.urlid.urlid[3:]) > 0) and (int(item.urlid.urlid[3:]) < 50):
					img = 'department'
				announce.append([img, item.author(), str(item.date()), str(item.id), item.__unicode__()])
				if i == 30:
					break
				i += 1
	return render_to_response('announcements.html', {
			'head_title': 'Ανακοινώσεις | ',
			'items': announce,
			'form': form,
			'id': id,
		}, context_instance = RequestContext(request))
