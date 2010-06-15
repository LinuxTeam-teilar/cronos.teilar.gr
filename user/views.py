# -*- coding: utf-8 -*-

from cronos.user.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

def getmail(request):
	if request.user.email[-21:] == 'notapplicablemail.com':
		mail = 'unset'
	elif request.user.get_profile().webmail_username:
		mail = request.user.get_profile().webmail_username + '@teilar.gr'
	else:
		''
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
	other_list = []
	other_list.append(['noc', 'teilar', 'career', 'linuxteam', 'school', 'pr', 'dionysos', 'library'])
	other_list.append(['cid50', 'cid0', 'cid51', 'cid52', request.user.get_profile().school, 'cid55', 'cid53', 'cid54'])
	other_list.append([])
	i = 0
	'''form_other = []
	for item in Id.objects.filter(urlid__in = other_list[1]).order_by('name'):
		try:
			if other_list[1][i] in request.user.get_profile().other_announcements.split(','):
				other_list[2].append('checked="yes"')
			else:
				other_list[2].append('')
		except:
			other_list[2].append('')
			pass
		form_other.append('<input type="checkbox" name="' + other_list[0][i] + '" id="id_' + other_list[0][i] + '" ' + other_list[2][i] + \
							' /><label for="id_' + other_list[0][i] + '">' + item.name + '</label>')
		i += 1

	form_teacher = []
	i = 0
	for item in Id.objects.filter(urlid__startswith='pid').order_by('name'):
		try:
			if item.urlid in request.user.get_profile().teacher_announcements.split(','):
				checked = 'checked="yes"'
			else:
				checked = ''
		except:
			checked = ''
			pass
		form_teacher.append('<input type="checkbox" name="' + item.urlid + '" id="id_' + item.urlid + '" ' + checked + \
							' /><label for="id_' + item.urlid + '">' + item.name + '</label>')
		i += 1
	msg = ''
	if request.method == 'POST':
		form = OtherAnnouncements(request.POST)
		
		msg = 'Η αλλαγή ήταν επιτυχής'
	else:
		form = OtherAnnouncements()'''
	
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
			'form_teacher': form_teacher,
		}, context_instance = RequestContext(request))
