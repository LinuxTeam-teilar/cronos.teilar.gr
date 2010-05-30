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

				'''add_record = [
					('objectclass', ['person','top','teilarstudent']),
					('cn', [request.POST.get('username')]),
					('firstName', [request.POST.get('first_name')]),
					('sn', [request.POST.get('lastname')]),
					('userPassword', [request.POST.get('password')]),
					('school', [request.POST.get('school')]),
					('semester', [request.POST.get('semester')]),
					('introductionYear', [request.POST.get('introduction_year')]),
					('registrationNumber', [request.POST.get('registrationNumber')]),
				]'''
				
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
	return render_to_response('signup.html', {
			'head_title': 'Εγγραφή | ',
			'form': form } )
