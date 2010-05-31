# -*- coding: utf-8 -*-

from cronos.signup.forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			try:
				from BeautifulSoup import BeautifulSoup
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
					('userName', request.POST.get('dionysos_username')),
					('pwd', request.POST.get('dionysos_password')),
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
				output = (b.getvalue()).decode('windows-1253')
				dionysos_username = request.POST.get('dionysos_username')
				dionysos_password = request.POST.get('dionysos_password')
				soup = BeautifulSoup(output)
				soup1 = BeautifulSoup(str(soup.findAll('table')[13]))
				#username = str(soup1.findAll('td')[1].contents[0])
				soup2 = BeautifulSoup(str(soup1.findAll('tr')[5]))
				last_name = str(soup2.findAll('td')[1].contents[0])
				soup2 = BeautifulSoup(str(soup1.findAll('tr')[6]))
				first_name = str(soup2.findAll('td')[1].contents[0])
				soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
				registration_number = str(soup2.findAll('td')[1].contents[0])
				soup2 = BeautifulSoup(str(soup1.findAll('tr')[9]))
				semester = str(soup2.findAll('td')[1].contents[0])
				soup2 = BeautifulSoup(str(soup1.findAll('tr')[8]))
				school = str(soup2.findAll('td')[1].contents[0])
				# missing introduction_year
				# missing declaration

				# login to eclass
				if request.POST.get('eclass_username'):
					b = StringIO.StringIO()
					login_form_seq = [
						('uname', 'cst01387'),
						('pass', 'h0m3b*yz'),
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
					# ...and then parse his lessons
					eclass_username = request.POST.get('eclass_username')
					eclass_password = request.POST.get('eclass_password')
				else:
					eclass_username = None
					eclass_password = None

				# login to webmail
				if request.POST.get('webmail_username'):
					b = StringIO.StringIO()
					cookie_file_name = os.tempnam('/tmp','webmail')
					login_form_data = urllib.urlencode(login('webmail'))
					conn.setopt(pycurl.FOLLOWLOCATION, 0)
					conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
					conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
					conn.setopt(pycurl.URL, 'http://myweb.teilar.gr')
					conn.setopt(pycurl.POST, 0)
					conn.perform()
					conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/redirect.php')
					conn.setopt(pycurl.POST, 1)
					conn.setopt(pycurl.POSTFIELDS, login_form_data)
					conn.setopt(pycurl.WRITEFUNCTION, b.write)
					conn.perform()
					conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
					conn.perform()
					webmail_username = request.POST.get('webmail_username')
					webmail_password = request.POST.get('webmail_password')
				else:
					webmail_username = None
					webmail_password = None

				# add to ldap

				import ldap
				from django.conf import settings
				import ldap.modlist as modlist
				
				l=ldap.initialize(settings.LDAP_URL)
				l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
		
				# before adding to ldap, check if user is already there
				if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'cn=%s' % (request.POST.get('username')),settings.SEARCH_FIELDS):
					template = get_template('signup.html')
					variables = Context({
						'head_title': 'Εγγραφή | ',
						'form': form,
						'msg': 'Ο χρήστης υπάρχει ήδη.'
					})
					output = template.render(variables)
					return HttpResponse(output)
				else:
					username = str(request.POST.get('username'))
					attrs = {}
					attrs['objectClass'] = ['person','top','teilarStudent']
					attrs['cn'] =  [username]
					attrs['sn'] = [last_name]
					attrs['firstName'] = [first_name]
					attrs['userPassword'] = [str(request.POST.get('password'))]
					attrs['school'] = [school]
					attrs['semester'] = [str(semester)]
					attrs['introductionYear'] = ['2004x']
					attrs['registrationNumber'] = [registration_number]
					#attrs['eclassUsername'] = [str(eclass_username)]
					#attrs['eclassPassword'] = [str(eclass_password)]
					attrs['dionysosUsername'] = [str(dionysos_username)]
					attrs['dionysosPassword'] = ['dio']
					#attrs['webmailUsername'] = [str(webmail_username)]
					#attrs['webmailPassword'] = [str(webmail_password)]
					print attrs
#					('declaration', declaration),
#					('eclassLessons', eclass_lessons),
#					('teacherAnnouncements', teacher_announcements),

					ldif = modlist.addModlist(attrs)
					l.add_s('cn=%s,ou=teilarStudents,dc=teilar,dc=gr' % (username), ldif)
					l.unbind_s()
				
				# in case there is no exception in the above, send the user to a welcome site
				template = get_template('welcome.html')
				variables = Context({
					'head_title': 'Καλώς Ήρθατε | ',
					'username': request.POST.get('username'),
					'eclass_username': eclass_username,
					'dionysos_username': dionysos_username,
					'mail': webmail_username,
					'first_name': first_name,
					'last_name': last_name,
					'semester': semester,
					'school': school,
					#'introduction_year': introduction_year,
					'registration_number': registration_number,
					#'declaration': declaration,
					#'eclass_lessons': eclass_lessons,
				})
				output = template.render(variables)
				return HttpResponse(output)
				
			except:
				template = get_template('signup.html')
				variables = Context({
					'head_title': 'Εγγραφή | ',
					'form': form,
					'msg': 'Παρουσιάστηκε Σφάλμα'
				})
				output = template.render(variables)
				return HttpResponse(output)
	else:
		form = SignupForm()
	template = get_template('signup.html')
	variables = Context({
		'head_title': 'Εγγραφή | ',
		'form': form,
	})
	output = template.render(variables)
	return HttpResponse(output)
