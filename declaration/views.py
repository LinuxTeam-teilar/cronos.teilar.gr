# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.declaration.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def declaration(request):
	declaration_full = request.user.get_profile().declaration.split(',')
	i = 3
	summary = declaration_full[:i]
	declaration_lessons = []
	while i <= len(declaration_full) - len(summary):
		declaration_lessons.append(declaration_full[i:i+6])
		i += 6
	msg = ''
	if request.method == 'POST':
		form = DeclarationForm(request.GET)
		from BeautifulSoup import BeautifulSoup
		import pycurl
		import StringIO
		import urllib
		import os
		import urlparse
		import base64

		conn = pycurl.Curl()

		try:
			# login to eclass
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
		}, context_instance = RequestContext(request))
