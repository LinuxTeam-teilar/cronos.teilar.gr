# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from cronos.announcements.forms import AnnouncementForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from django.template import Context,RequestContext, Template
from django.template.loader import render_to_string


@login_required
def announcements(request):
	form = AnnouncementForm(request.GET)
	if (len(str(request.GET.get('announceid'))) != 4):
		db = Announcements.objects.filter(id__exact = request.GET.get('announceid'))
		for item in db:
			announce_body = [item.author(), str(item.date()), item.__unicode__(), item.get_absolute_url(), item.body()]
		return render_to_response('announcements.html', {
				'head_title': 'Ανακοινώσεις | ',
				'content': announce_body,
			}, context_instance = RequestContext(request))
	else:
		announce_list = []
		i = 0
		for item in Announcements.objects.order_by('-date_fetched')[:30]:
			announce_list.append([])
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
			announce1 = [img, item.author(), str(item.date()), str(item.id), item.__unicode__()]
			for j in xrange(5):
				announce_list[i].append(announce1[j][:])
			i += 1
		return render_to_response('announcements.html', {
				'head_title': 'Ανακοινώσεις | ',
				'items': announce_list,
				'form': form,
			}, context_instance = RequestContext(request))
