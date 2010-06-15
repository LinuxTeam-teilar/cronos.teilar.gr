# -*- coding: utf-8 -*-

from cronos.user.forms import *
from cronos.signup.views import Sha1Password
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
import ldap
import ldap.modlist as modlist


def getmail(request):
	if request.user.email[-21:] == 'notapplicablemail.com':
		mail = 'unset'
	else:
		mail = request.user.email
	return mail

def getschool(request):
	for item in Id.objects.filter(urlid__exact = request.user.get_profile().school):
		school = str(item.name)
	return school

@login_required
def user(request):
	return render_to_response('user.html', {
			'mail': getmail(request),
			'school': getschool(request),
		}, context_instance = RequestContext(request))

@login_required
def user_settings(request):
	msg = ''
	cronos_form = CronosForm()
	dionysos_form = DionysosForm()
	eclass1_form = Eclass1Form()
	webmail_form = WebmailForm()
	email_form = EmailForm()
	if request.method == 'POST':
		if request.POST.get('old_password'):
			cronos_form = CronosForm(request.POST)
			if cronos_form.is_valid():
				if request.POST.get('password1') == request.POST.get('password2'):
					user = User.objects.get(username = request.user.username)
					if user.check_password(request.POST.get('old_password')):
						print 'ok'
						try:
							l = ldap.initialize(settings.LDAP_URL)
							l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
							mod_attrs = [ (ldap.MOD_ADD, 'userPassword', Sha1Password(request.POST.get('password1'))) ]
							l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
							l.unbind_s()
							
							user.set_password(request.POST.get('password1'))
							user.save()

							msg = 'Η αλλαγή του κωδικού πραγματοποιήθηκε με επιτυχία'
						except:
							msg = 'Παρουσιάστηκε Σφάλμα'
					else:
						print 'not ok'
						msg = 'Ο τρέχων κωδικός που δώσατε είναι λανθασμένος, παρακαλούμε ξαναπροσπαθήστε'
				else:
					msg = 'Οι κωδικοί δεν ταιριάζουν, παρακαλούμε ξαναπροσπαθήστε'
		'''if request.POST.get('dionysos_username'):
			dionysos_form = DionysosForm(request.POST)
			if dionysos_form.is_valid():
				try:
					dionysos_login(0, request.POST.get('dionysos_username'), request.POST.get('dionysos_password'))

					l = ldap.initialize(settings.LDAP_URL)
					l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
					mod_attrs = [(ldap.MOD_DELETE, 'dionysosUsername', None)]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					mod_attrs = [(ldap.MOD_DELETE, 'dionysosPassword', None)]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					mod_attrs = [(ldap.MOD_ADD, 'dionysosUsername', base64.b64encode(request.POST.get('dionysos_password')))]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()

					u.dionysos_password = (request.POST.get('dionysos_username'))
					u.dionysos
					u.save()
					
				msg = 'Η ανανέωση των στοιχείων για το dionysos ήταν επιτυχής'
		if eclass1_form.is_valid():
			msg = 'Η ανανέωση των στοιχείων για το eclass ήταν επιτυχής'
		if webmail_form.is_valid():
			msg = 'Η ανανέωση των στοιχείων για το webmail ήταν επιτυχής'''
		if request.POST.get('email'):
			email_form = EmailForm(request.POST)
			if email_form.is_valid():
				u = User.objects.get(username = request.user.username)
				u.email = request.POST.get('email')
				u.save()
				msg = 'Η ανανέωση του email σας ήταν επιτυχής'

	else:
		cronos_form = CronosForm()
		dionysos_form = DionysosForm()
		eclass1_form = Eclass1Form()
		webmail_form = WebmailForm()
		email_form = EmailForm()
	
	# update dionysos' declaration
	'''if request.method == 'POST':
		form = DeclarationForm(request.GET)
		from BeautifulSoup import BeautifulSoup
		import base64
		import os
		import pycurl
		import StringIO
		import urllib
		import urlparse

		conn = pycurl.Curl()

		try:
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
			conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&')
			conn.setopt(pycurl.POST, 1)
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.COOKIE, cookie_file_name)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = (b.getvalue()).decode('windows-1253')
			soup = BeautifulSoup(output)
			soup1 = BeautifulSoup(str(soup.findAll('table')[14]))

			# parse user's announcement
			declaration_new = []
			declaration_new.append([])
			for item in soup1.findAll('td', 'error'):
				declaration_new[0].append(str(item.contents[0]))
				k = 8
			for i in xrange(len(soup1.findAll('span', 'underline'))):
				declaration_new.append([
					str(soup1.findAll('td')[k].contents[2][6:]),
					str(soup1.findAll('span', 'underline')[i].contents[0]).strip(),
					str(soup1.findAll('td')[k+2].contents[0]),
					str(soup1.findAll('td')[k+3].contents[0]),
					str(soup1.findAll('td')[k+4].contents[0]),
					str(soup1.findAll('td')[k+5].contents[0])
				])
				k += 7

			# change values to ldap
			import ldap
			import ldap.modlist as modlist
			from django.conf import settings

			l = ldap.initialize(settings.LDAP_URL)
			l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)

			mod_attrs = [ (ldap.MOD_DELETE, 'declaration', None) ]
			l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				
			mod_attrs = []
			for i in xrange(len(declaration_new)):
				mod_attrs.append((ldap.MOD_ADD, 'declaration', ','.join(declaration_new[i])))
			l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
		
			l.unbind_s()

			# change values to user profile
			from cronos.user.models import LdapProfile

			declaration_new_list = []
			for item in declaration_new:
				declaration_new_list += item
			u = LdapProfile.objects.get(user__username = request.user.username)
			u.declaration = ','.join(declaration_new_list)
			u.save()
						
			msg = 'Η δήλωσή σας ανανεώθηκε'

		except TypeError:
			msg = 'Παρουσιάστηκε σφάλμα'
	else:
		form = DeclarationForm()

		return  render_to_response('declaration.html', {
						'summary': summary,
						'declaration_lessons': declaration_lessons,
						'msg': msg,
						'form': form,
				}, context_instance = RequestContext(request))'''

	if request.method == 'POST':
		form_teacher = TeacherAnnouncementsForm(request.POST)
		if form_teacher.is_valid():
			print 'form is valid'
	else:
		form_teacher = TeacherAnnouncementsForm()

	return render_to_response('settings.html', {
			'mail': getmail(request),
			'cronos_form': cronos_form,
			'dionysos_form': dionysos_form,
			'eclass1_form': eclass1_form,
			'webmail_form': webmail_form,
			'email_form': email_form,
			'msg': msg,
			'form_teacher': form_teacher,
		}, context_instance = RequestContext(request))
