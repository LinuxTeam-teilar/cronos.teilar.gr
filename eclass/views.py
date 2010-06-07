# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.announcements.models import *
import pycurl
import StringIO
import urllib
import os
import urlparse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
import base64

@login_required
def eclass(request):
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	login_form_seq = [
		('uname', request.user.get_profile().eclass_username),
		('pass', base64.b64decode(request.user.get_profile().eclass_password)),
		('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82')
	]
	login_form_data = urllib.urlencode(login_form_seq)
	conn.setopt(pycurl.FOLLOWLOCATION, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.URL, 'http://e-class.teilar.gr/index.php')
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)
	headers = []
	i = 0
 	for item in soup.findAll('th', 'persoBoxTitle'):
		if i !=2 and i != 5:
			headers.append(item.contents[0])
		i += 1

	soup1 = BeautifulSoup(str(soup.findAll('tr', 'odd')[3]))
	deadlines = []
	i = 0
	for item in soup1.findAll('li', 'category'):
		lesson = item.contents[0]
		title = soup1.findAll('a', 'square_bullet2')[i].contents[0].contents[0]
		date = soup1.findAll('p', 'content_pos')[i].b.contents[0]
		status = soup1.findAll('span')[i].contents[0]
		deadlines.append([lesson, title, date, status])
		i += 1

	soup1 = BeautifulSoup(str(soup.findAll('tr', 'odd')[4]))
	documents = []
	i = 0
	j = 0
	for item in soup1.findAll('li'):
		if item in soup1.findAll('li', 'category'):
			lesson = item.contents[0]
			i += 1
		else:
			title = soup1.findAll('a', 'square_bullet2')[j]
			j += 1
			documents.append([lesson, title])
	
	eclass_lessons = []
	eclass_lessons_ids = request.user.get_profile().eclass_lessons.split(',')
	for item in Id.objects.filter(urlid__in = eclass_lessons_ids):
		eclass_lessons.append([item.urlid.strip(), item.name[9:]])

	eclass_announcements = []
	for item in Announcements.objects.filter(urlid__urlid__in = eclass_lessons_ids).order_by('-date_fetched')[:15]:
		eclass_announcements.append([item.urlid.name[9:], item.title])

	return render_to_response('eclass.html', {
			'headers': headers,
			'eclass_lessons': eclass_lessons,
			'eclass_announcements': eclass_announcements,
			'deadlines': deadlines,
			'documents': documents,
		}, context_instance = RequestContext(request))
