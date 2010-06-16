# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.dionysos.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def dionysos(request):
	msg = ''
	summary = ''
	declaration_lessons = []
	if request.user.get_profile().declaration:
		declaration_full = request.user.get_profile().declaration.split(',')
		i = 3
		summary = declaration_full[:i]
		while i <= len(declaration_full) - len(summary):
			declaration_lessons.append(declaration_full[i:i+6])
			i += 6
	else:
		msg = 'Η δήλωσή σας είναι κενή'

	return  render_to_response('dionysos.html', {
			'summary': summary,
			'declaration_lessons': declaration_lessons,
			'msg': msg,
		}, context_instance = RequestContext(request))

'''@login_required
def grades_notready(request):
	from BeautifulSoup import BeautifulSoup
	from cronos.login.teilar import *
	import base64

	link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
	dionysos_login(0, request.user.get_profile().dionysos_username, decryptPassword(request.user.get_profile().dionysos_password))
	output = dionysos_login(link, 0, 0)
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


#	return render_to_response('grades.html', {
#			'lessons': lessons,
#		}, context_instance = RequestContext(request))'''
