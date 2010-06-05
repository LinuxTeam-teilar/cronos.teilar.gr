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
		for item in Announcements.objects.filter(id__exact = request.GET.get('announceid')):
			all_announcements = [item.author(), str(item.date()), item.__unicode__(), item.get_absolute_url(), item.body()]
		id = request.GET.get('announceid')
	else:
		form = AnnouncementForm()
		all_announcements = []
		all_announcements_ids = [request.user.get_profile().school]
		try:
			all_announcements_ids += request.user.get_profile().eclass_lessons.split(',')
			all_announcements_ids += request.user.get_profile().other_announcements.split(',')
			all_announcements_ids += request.user.get_profile().teacher_announcements.split(',')
		except:
			pass
		print all_announcements_ids
		for item in Announcements.objects.filter(urlid__urlid__in = all_announcements_ids).order_by('-date_fetched')[:30]:
				print item
				img = item.urlid.urlid
				if (item.urlid.urlid[:3] != 'pid') and (item.urlid.urlid[:3] != 'cid'):
					img = 'eclass'
				if (item.urlid.urlid[:3] == 'pid'):
					img = 'teacher'
				if (item.urlid.urlid == 'pid323') or (item.urlid.urlid == 'pid324'):
					img = item.urlid.urlid
				if (item.urlid.urlid == 'pid326') or (item.urlid.urlid == 'pid327'):
					img == 'meeting'
				if (item.urlid.urlid[:3] == 'cid') and (int(item.urlid.urlid[3:]) > 0) and (int(item.urlid.urlid[3:]) < 50):
					img = 'department'
				all_announcements.append([img, item.author(), str(item.date()), str(item.id), item.__unicode__()])
	return render_to_response('announcements.html', {
			'head_title': 'Ανακοινώσεις | ',
			'items': all_announcements,
			'form': form,
			'id': id,
		}, context_instance = RequestContext(request))
