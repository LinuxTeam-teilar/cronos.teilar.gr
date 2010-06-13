# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.dionysos.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def declaration(request):
	msg = ''
	summary = ''
	declaration_lessons = []
	declaration_full = request.user.get_profile().declaration.split(',')
	if request.user.get_profile().declaration:
		declaration_full = request.user.get_profile().declaration.split(',')
		i = 3
		summary = declaration_full[:i]
		while i <= len(declaration_full) - len(summary):
			declaration_lessons.append(declaration_full[i:i+6])
			i += 6
	else:
		msg = 'Η δήλωσή σας είναι κενή'
	return  render_to_response('declaration.html', {
			'summary': summary,
			'declaration_lessons': declaration_lessons,
			'msg': msg,
		}, context_instance = RequestContext(request))

@login_required
def grades_notready(request):
	from BeautifulSoup import BeautifulSoup
	import base64
	import pycurl
	import StringIO
	import urllib
	import os
	import urlparse

	conn = pycurl.Curl()

	# login to dionysos
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	cookie_file_name = os.tempnam('/tmp','dionysos')
	login_form_seq = [
		('userName', request.user.get_profile().dionysos_username),
		('pwd', base64.b64decode(request.user.get_profile().dionysos_password)),
		('submit1', '%C5%DF%F3%EF%E4%EF%F2'),
		('loginTrue', 'login')
	]
	login_form_data = urllib.urlencode(login_form_seq)
	conn.setopt(pycurl.FOLLOWLOCATION, 1)
	conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
	conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
	conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/')
	conn.setopt(pycurl.POST, 0)
	conn.perform()
	conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/login.asp')
	conn.setopt(pycurl.POST, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&')
	conn.setopt(pycurl.POST, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.COOKIE, cookie_file_name)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = (b.getvalue()).decode('windows-1253')
	soup = BeautifulSoup(output)
	all = []
	i = 0
	while i < len(soup.findAll('table')[13].findAll('td')):
		item = soup.findAll('td')[i]
		if item in soup.findAll('td', 'groupHeader'):
			all.append([item.contents[0]])
		if item in soup.findAll('td', 'topBorderLight'):
			all.append([
				str(item.contents[0]),
				str(soup.findAll('td')[i+1].contents[0]),
				str(soup.findAll('td')[i+2].contents[0]),
				str(soup.findAll('td')[i+3].contents[0]),
				str(soup.findAll('td')[i+4].contents[0]),
				str(soup.findAll('td')[i+5].contents[0]),
				str(soup.findAll('td')[i+6].contents[0].i.contents[0]),
			])
			i += 6
		i += 1

	return render_to_response('grades.html', {
			'all': all,
		}, context_instance = RequestContext(request))

def grades(request):
	return render_to_response('grades.html', {
		}, context_instance = RequestContext(request))
