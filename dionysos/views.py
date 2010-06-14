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
	lessons = []
	i = 0
	while i < len(soup.findAll('table')[13].findAll('td')):
		item0 = soup.findAll('table')[13].findAll('td')[i]
		item = soup.findAll('table')[13].findAll('td')
		if item0 in soup.findAll('td', 'groupHeader'):
			lessons.append([item0.contents[0]])
		if item0 in soup.findAll('td', 'topBorderLight'):
			year = str(item[i+6].contents[0].i.contents[0])
			year = year[:10] + year[-9:]
			if year =='--':
				year = '-'
			lessons.append([
				str(item0.contents[0]),
				str(item[i+1].contents[0]),
				str(item[i+2].contents[0]),
				str(item[i+3].contents[0]),
				str(item[i+4].contents[0]),
				str(item[i+5].span.contents[0]),
				year,
			])
			try:
				if item[i+9].contents[1][-3:] == '(Θ)' or item[i+9].contents[1][-3:] == '(Ε)':
					year = str(item[i+14].contents[0].i.contents[0])
					year = year[:10] + year[-9:]
					lessons.append([
						str(item[i+9].contents[1]),
						'',
						str(item[i+10].i.contents[0]),
						str(item[i+11].contents[0]),
						str(item[i+12].contents[0]),
						str(item[i+13].contents[0]),
						year,
					])
					year = str(item[i+22].contents[0].i.contents[0])
					year = year[:10] + year[-9:]
					lessons.append([
						str(item[i+17].contents[1]),
						'',
						str(item[i+18].i.contents[0]),
						str(item[i+19].contents[0]),
						str(item[i+20].contents[0]),
						str(item[i+21].contents[0]),
						year,
					])
					i += 11
			except:
				pass
			i += 6
		try:
			if item0.contents[0][:6] == 'Σύνολα':
				lessons.append([
					str(item0.b.contents[0]),
					str(item[i+1].contents[1].contents[0]).strip(),
					str(item[i+1].contents[3].contents[0]).strip(),
					str(item[i+1].contents[5].contents[0]).strip(),
					str(item[i+1].contents[7].contents[0]).strip(),
				])
				i += 1
		except:
			pass
		i += 1

	return render_to_response('grades.html', {
			'lessons': lessons,
		}, context_instance = RequestContext(request))

def grades(request):
	return render_to_response('grades.html', {
		}, context_instance = RequestContext(request))
