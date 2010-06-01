# -*- coding: utf-8 -*-

from cronos.signup.forms import *
from django.http import HttpResponse
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard

class SignupWizard(FormWizard):
	def done(self, request, form_list):
		username = str([form.cleaned_data for form in form_list][0]['username'])
		password = str([form.cleaned_data for form in form_list][0]['password'])
		dionysos_username = str([form.cleaned_data for form in form_list][1]['dionysos_username'])
		dionysos_password = str([form.cleaned_data for form in form_list][1]['dionysos_password'])
		eclass_username = str([form.cleaned_data for form in form_list][2]['eclass_username'])
		eclass_password = str([form.cleaned_data for form in form_list][2]['eclass_password'])
		webmail_username = str([form.cleaned_data for form in form_list][3]['webmail_username'])
		webmail_password = str([form.cleaned_data for form in form_list][3]['webmail_password'])
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
				('userName', dionysos_username),
				('pwd', dionysos_password),
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
			# missing declaration'''
			
			# login to eclass
			if eclass_username:
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

			# login to webmail
			if webmail_username:
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

			# add to ldap
			import ldap
			from django.conf import settings
			import ldap.modlist as modlist
			
			l=ldap.initialize(settings.LDAP_URL)
			l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
	
			# before adding to ldap, check if user is already there
			if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'cn=%s' % (username),settings.SEARCH_FIELDS):
				return self.render(self.get_form(0), request, 0, context = {
						'msg': 'Ο χρήστης υπάρχει ήδη.'
					})
			else:
				attrs = {}
				attrs['objectClass'] = ['person','top','teilarStudent']
				attrs['cn'] =  [username]
				attrs['sn'] = [last_name]
				attrs['firstName'] = [first_name]
				attrs['userPassword'] = [password]
				attrs['school'] = [school]
				attrs['semester'] = [semester]
				attrs['introductionYear'] = ['2004x']
				attrs['registrationNumber'] = [registration_number]
				attrs['eclassUsername'] = [eclass_username]
				attrs['eclassPassword'] = ['eclass']#str(eclass_password)]
				attrs['dionysosUsername'] = [str(dionysos_username)]
				attrs['dionysosPassword'] = ['dio']
				#attrs['webmailUsername'] = [str(webmail_username)]
				#attrs['webmailPassword'] = [str(webmail_password)]
				#('declaration', declaration),
				#('eclassLessons', eclass_lessons),
				#('teacherAnnouncements', teacher_announcements),

				ldif = modlist.addModlist(attrs)
				l.add_s('cn=%s,ou=teilarStudents,dc=teilar,dc=gr' % (username), ldif)
				l.unbind_s()
			
			# in case there is no exception in the above, send the user to a welcome site
			template = get_template('welcome.html')
			variables = Context({
				'head_title': 'Καλώς Ήρθατε | ',
				'username': username,
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
				'form': [form.cleaned_data for form in form_list]
			})
			output = template.render(variables)
			return HttpResponse(output)
		except:
			return self.render(self.get_form(0), request, 0, context = {
					'msg': 'Παρουσιάστηκε Σφάλμα',
				})

	def render_template(self, request, form, previous_fields, step, context=None):
		context = context or {}
		context.update(self.extra_context)
		return render_to_response(self.get_template(step), dict(context,
				step_field=self.step_field_name,
				step0=step,
				step=step + 1,
				step_count=self.num_steps(),
				form=form,
				previous_fields=previous_fields,
				head_title = 'Εγγραφή | ',
			), context_instance=RequestContext(request))

	def get_template(self, step):
		return '/home/tampakrap/Source_Code/ptixiaki/cronos/templates/signup.html'
