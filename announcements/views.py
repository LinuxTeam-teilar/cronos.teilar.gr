# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from cronos.announcements.forms import AnnouncementForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def announcements(request):
	id = ''
	if (request.GET.get('announceid')):
		form = AnnouncementForm(request.GET)
		for item in Announcements.objects.filter(id__exact = request.GET.get('announceid')):
			date = str(item.date()).split(' ')[0].split('-')
			hour = str(item.date()).split(' ')[1].split(':')
			date = date[2] + '/' + date[1] + '/' + date[0] + ', ' + hour[0] + ':' + hour[1]
			all_announcements = [item.author(), item.get_absolute_url(), item.__unicode__(), date, item.body()]
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
		for item in Announcements.objects.filter(urlid__urlid__in = all_announcements_ids).order_by('-date_fetched')[:30]:
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
				date = str(item.date()).split(' ')[0].split('-')
				hour = str(item.date()).split(' ')[1].split(':')
				date = date[2] + '/' + date[1] + '/' + date[0] + ', ' + hour[0] + ':' + hour[1]
				if len(item.author()) > 30:
					length = 'big'
				else:
					length = ''
				all_announcements.append([item.author(), length, img, str(item.id), item.__unicode__(), date])
	return render_to_response('announcements.html', {
			'items': all_announcements,
			'form': form,
			'id': id,
		}, context_instance = RequestContext(request))
