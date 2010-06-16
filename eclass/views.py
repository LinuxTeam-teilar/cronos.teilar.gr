# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.announcements.models import *
from cronos.login.encryption import decryptPassword
from cronos.login.teilar import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def eclass(request):
	try:
		output = eclass_login(request.user.get_profile().eclass_username, decryptPassword(request.user.get_profile().eclass_password))
		soup = BeautifulSoup(output)

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
				title = soup1.findAll('a', 'square_bullet2')[j].contents[0].contents[0].split(' - (')[0]
				date = soup1.findAll('a', 'square_bullet2')[j].contents[0].contents[0].split(' - (')[1][:-1]
				documents.append([lesson, title, date])
				j += 1

	except:
		deadlines = ''
		documents = ''
		pass

	eclass_lessons = []
	for item in Id.objects.filter(urlid__in = request.user.get_profile().eclass_lessons.split(',')):
		eclass_lessons.append([item.urlid.strip(), item.name[9:]])

	return render_to_response('eclass.html', {
			'headers': ['ΤΑ ΜΑΘΗΜΑΤΑ ΜΟΥ', 'ΟΙ ΔΙΟΡΙΕΣ ΜΟΥ', 'ΤΑ ΤΕΛΕΥΤΑΙΑ ΜΟΥ ΕΓΓΡΑΦΑ'],
			'eclass_lessons': eclass_lessons,
			'deadlines': deadlines,
			'documents': documents,
		}, context_instance = RequestContext(request))
