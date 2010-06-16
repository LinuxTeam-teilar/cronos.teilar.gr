# -*- coding: utf-8 -*-

from cronos.login.encryption import sha1Password, encryptPassword, decryptPassword
from cronos.login.teilar import *
from cronos.user.forms import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
import ldap
import ldap.modlist as modlist


def getmail(request):
	if request.user.email[-13:] == 'emptymail.com':
		mail = ''
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
	declaration_form = DeclarationForm()
	if request.method == 'POST':
		if request.POST.get('old_password'):
			cronos_form = CronosForm(request.POST)
			if cronos_form.is_valid():
				if request.POST.get('password1') == request.POST.get('password2'):
					user = User.objects.get(username = request.user.username)
					if user.check_password(request.POST.get('old_password')):
						try:
							l = ldap.initialize(settings.LDAP_URL)
							l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
							mod_attrs = [(ldap.MOD_DELETE, 'userPassword', None)]
							l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
							mod_attrs = [(ldap.MOD_ADD, 'userPassword', sha1Password(request.POST.get('password1')))]
							l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
							l.unbind_s()
							
							user.set_password(request.POST.get('password1'))
							user.save()

							msg = 'Η αλλαγή του κωδικού πραγματοποιήθηκε με επιτυχία'
						except:
							msg = 'Παρουσιάστηκε Σφάλμα'
					else:
						msg = 'Ο τρέχων κωδικός που δώσατε είναι λανθασμένος, παρακαλούμε ξαναπροσπαθήστε'
				else:
					msg = 'Οι κωδικοί δεν ταιριάζουν, παρακαλούμε ξαναπροσπαθήστε'
		if request.POST.get('dionysos_username'):
			dionysos_form = DionysosForm(request.POST)
			if dionysos_form.is_valid():
				try:
					dionysos_login(0, request.POST.get('dionysos_username'), request.POST.get('dionysos_password'))
				except:
					msg = 'Τα στοιχεία που δώσατε δεν επαληθεύτηκαν'

				try:
					l = ldap.initialize(settings.LDAP_URL)
					l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
					mod_attrs = modlist.modifyModlist({'dionysosUsername': [request.user.get_profile().dionysos_username]}, {'dionysosUsername': [str(request.POST.get('dionysos_username'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					mod_attrs = modlist.modifyModlist({'dionysosPassword': [request.user.get_profile().dionysos_password]}, {'dionysosPassword': [encodePassword(request.POST.get('dionysos_password'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()

					user = LdapProfile.objects.get(user__username = request.user.username)
					user.dionysos_username = request.POST.get('dionysos_username')
					user.dionysos_password = encodePassword(request.POST.get('dionysos_password'))
					user.save()
					
					msg = 'Η ανανέωση των στοιχείων για το dionysos ήταν επιτυχής'
				except AttributeError:
					msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('eclass_username')
			eclass1_form = Eclass1Form(request.POST)
			if eclass1_form.is_valid():
				try:
					eclass_login(request.POST.get('eclass_username'), request.POST.get('eclass_password'))
				except:
					msg = 'Τα στοιχεία που δώσατε δεν επαληθεύτηκαν'

				try:
					l = ldap.initialize(settings.LDAP_URL)
					l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
					mod_attrs = modlist.modifyModlist({'eclassUsername': [str(request.user.get_profile().eclass_username)]}, {'eclassUsername': [str(request.POST.get('eclass_username'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					mod_attrs = modlist.modifyModlist({'eclassPassword': [request.user.get_profile().eclass_password]}, {'eclassPassword': [encodePassword(request.POST.get('eclass_password'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()

					user = LdapProfile.objects.get(user__username = request.user.username)
					user.eclass_username = request.POST.get('eclass_username')
					user.eclass_password = encodePassword(request.POST.get('eclass_password'))
					user.save()
					
					msg = 'Η ανανέωση των στοιχείων για το e-class ήταν επιτυχής'
				except:
					msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('webmail_username'):
			webmail_form = WebmailForm(request.POST)
			if webmail_form.is_valid():
				try:
					webmail_login(0, request.POST.get('webmail_username'), request.POST.get('webmail_password'))
				except:
					msg = 'Τα στοιχεία που δώσατε δεν επαληθεύτηκαν'

				try:
					l = ldap.initialize(settings.LDAP_URL)
					l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
					mod_attrs = modlist.modifyModlist({'webmailUsername': [request.user.get_profile().webmail_username]}, {'webmailUsername': [str(request.POST.get('webmail_username'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					mod_attrs = modlist.modifyModlist({'webmailPassword': [request.user.get_profile().webmail_password]}, {'webmailPassword': [encodePassword(request.POST.get('webmail_password'))]})
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()

					user = LdapProfile.objects.get(user__username = request.user.username)
					user.webmail_username = request.POST.get('webmail_username')
					user.webmail_password = encodePassword(request.POST.get('webmail_password'))
					user.save()
					
					msg = 'Η ανανέωση των στοιχείων για το webmail ήταν επιτυχής'
				except:
					msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('email'):
			email_form = EmailForm(request.POST)
			if email_form.is_valid():
				l = ldap.initialize(settings.LDAP_URL)
				l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
				mod_attrs = modlist.modifyModlist({'cronosEmail': [getmail(request)]}, {'cronosEmail': [str(request.POST.get('email'))]})
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				l.unbind_s()
				
				u = User.objects.get(username = request.user.username)
				u.email = request.POST.get('email')
				u.save()
				msg = 'Η ανανέωση του email σας ήταν επιτυχής'
		if request.POST.get('declaration'):
			declaration_form = DeclarationForm(request.GET)
			link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
			dionysos_login(0, request.user.get_profile().dionysos_username, decodePassword(request.user.get_profile().dionysos_password))
	else:
		cronos_form = CronosForm()
		dionysos_form = DionysosForm()
		eclass1_form = Eclass1Form()
		webmail_form = WebmailForm()
		email_form = EmailForm()
		declaration_form = DeclarationForm()
	
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

	return render_to_response('settings.html', {
			'mail': getmail(request),
			'cronos_form': cronos_form,
			'dionysos_form': dionysos_form,
			'eclass1_form': eclass1_form,
			'webmail_form': webmail_form,
			'email_form': email_form,
			'declaration_form': declaration_form,
			'msg': msg,
		}, context_instance = RequestContext(request))
