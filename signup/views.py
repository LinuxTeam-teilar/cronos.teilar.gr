# -*- coding: utf-8 -*-

from cronos.signup.forms import *
from cronos.announcements.models import Id
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard
import base64
import hashlib
import os

def Sha1Password(password):
	from base64 import encodestring as encode
	salt = os.urandom(4)
	h = hashlib.sha1(password)
	h.update(salt)
	return "{SSHA}" + encode(h.digest() + salt)

class SignupWizard(FormWizard):
	def done(self, request, form_list):
		msg = ''
		dionysos_username = str([form.cleaned_data for form in form_list][0]['dionysos_username'])
		dionysos_password = base64.b64encode(str([form.cleaned_data for form in form_list][0]['dionysos_password']))
		eclass_username = str([form.cleaned_data for form in form_list][1]['eclass_username'])
		if eclass_username:
			eclass_password = base64.b64encode(str([form.cleaned_data for form in form_list][1]['eclass_password']))
		else:
			eclass_username = ''
		webmail_username = str([form.cleaned_data for form in form_list][2]['webmail_username'])
		if webmail_username:
			webmail_password = base64.b64encode(str([form.cleaned_data for form in form_list][2]['webmail_password']))
		else:
			webmail_username = ''
		username = str([form.cleaned_data for form in form_list][3]['username'])
		password1 = (str([form.cleaned_data for form in form_list][3]['password1']))
		password2 = (str([form.cleaned_data for form in form_list][3]['password2']))
		try:
			if password1 != password2:
				from random import choice
				import string
				dionysos_password = ''.join([choice(string.printable) for i in range(20)])
				msg = 'Ο κωδικός δεν επαληθεύτηκε'
			else:
				password = Sha1Password(str([form.cleaned_data for form in form_list][0]['password1']))
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
				('pwd', base64.b64decode(dionysos_password)),
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
			soup2 = BeautifulSoup(str(soup1.findAll('tr')[5]))
			last_name = str(soup2.findAll('td')[1].contents[0])
			soup2 = BeautifulSoup(str(soup1.findAll('tr')[6]))
			first_name = str(soup2.findAll('td')[1].contents[0])
			soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
			registration_number = str(soup2.findAll('td')[1].contents[0])
			soup2 = BeautifulSoup(str(soup1.findAll('tr')[9]))
			semester = str(soup2.findAll('td')[1].contents[0])
			soup2 = BeautifulSoup(str(soup1.findAll('tr')[8]))
			school = str(soup2.findAll('td')[1].contents[0]).strip()
			soup2 = BeautifulSoup(str(soup.findAll('table')[15]))
			# introduction year is in type first_year - next_year season
			# if season is 'Εαρινό' we parse the second_year, else the first_year
			season = str(soup2.findAll('span','tablecell')[1].contents[0])[:2]
			if season == 'Ε':
				year = str(soup2.findAll('span','tablecell')[0].contents[0].split('-')[1])
			else:
				year = str(soup2.findAll('span','tablecell')[0].contents[0].split('-')[0])
			introduction_year = year + season
			try:
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

				declaration = []
				declaration.append([])
				for item in soup1.findAll('td', 'error'):
					declaration[0].append(str(item.contents[0]))
				k = 8
				for i in xrange(len(soup1.findAll('span', 'underline'))):
					declaration.append([
						str(soup1.findAll('td')[k].contents[2][6:]),
						str(soup1.findAll('span', 'underline')[i].contents[0]).strip(),
						str(soup1.findAll('td')[k+2].contents[0]),
						str(soup1.findAll('td')[k+3].contents[0]),
						str(soup1.findAll('td')[k+4].contents[0]),
						str(soup1.findAll('td')[k+5].contents[0])
					])
					k += 7
			except:
				declaration = ''
				pass

			# login to eclass
			if eclass_username:
				b = StringIO.StringIO()
				login_form_seq = [
					('uname', eclass_username),
					('pass', base64.b64decode(eclass_password)),
					('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82')
				]
				login_form_data = urllib.urlencode(login_form_seq)
				conn.setopt(pycurl.FOLLOWLOCATION, 1)
				conn.setopt(pycurl.POSTFIELDS, login_form_data)
				conn.setopt(pycurl.URL, 'http://e-class.teilar.gr/index.php')
				conn.setopt(pycurl.WRITEFUNCTION, b.write)
				conn.perform()
				output = unicode(b.getvalue(), 'utf-8', 'ignore')
				soup = BeautifulSoup(output).find('table', 'FormData')
				i = 0
				eclass_lessons = []
				for item in soup.findAll('a'):
					if (i % 2 == 0):
						eclass_lessons.append(str(item.contents[0]).split('-')[0].strip())
					i += 1

			# login to webmail
			if webmail_username:
				b = StringIO.StringIO()
				cookie_file_name = os.tempnam('/tmp','webmail')
				login_form_seq = [
					('login_username', webmail_username),
					('secretkey', base64.b64decode(webmail_password)),
					('js_autodetect_results', '1'),
					('just_logged_in', '1')
				]
				login_form_data = urllib.urlencode(login_form_seq)
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
			from django.conf import settings
			import ldap
			import ldap.modlist as modlist
			
			l=ldap.initialize(settings.LDAP_URL)
			l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
	
			# before adding to ldap, check if user is already there
			if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'cn=%s' % (username),settings.SEARCH_FIELDS) or \
				l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'dionysosUsername=%s' % (dionysos_username),settings.SEARCH_FIELDS):
				return self.render(self.get_form(0), request, 0, context = {
						'msg': 'Ο χρήστης υπάρχει ήδη.'
					})
			else:
				attrs = {}
				attrs['objectClass'] = ['person','top','teilarStudent', 'posixAccount']
				attrs['uid'] =  [username]
				attrs['sn'] = [last_name]
				attrs['cn'] = [first_name]
				attrs['userPassword'] = [password]
				# add cid instead of full name in school attr
				db = Id.objects.filter(name__exact = (school))
				for item in db:
					cid = str(item.urlid)
				attrs['school'] = [cid]
				attrs['semester'] = [semester]
				attrs['introductionYear'] = [introduction_year]
				attrs['registrationNumber'] = [registration_number]
				attrs['dionysosUsername'] = [dionysos_username]
				attrs['dionysosPassword'] = [dionysos_password]
				if declaration:
					attrs['declaration'] = []
					for i in xrange(len(declaration)):
						attrs['declaration'].append(','.join(declaration[i]))
				if eclass_username:
					attrs['eclassUsername'] = [eclass_username]
					attrs['eclassPassword'] = [eclass_password]
					attrs['eclassLessons'] = eclass_lessons
				if webmail_username:
					attrs['webmailUsername'] = [webmail_username]
					attrs['webmailPassword'] = [webmail_password]
				attrs['homeDirectory'] = ['/home/' + username]
				attrs['gidNumber'] = ['100'] # 100 is the users group in linux
				results = l.search_s(settings.SEARCH_DN, ldap.SCOPE_SUBTREE, 'uid=*', ['uidNumber'])
				uids = []
				for item in results:
					uids.append(int(item[1]['uidNumber'][0]))
				attrs['uidNumber'] = [str(max(uids) + 1)]

				ldif = modlist.addModlist(attrs)
				l.add_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (username), ldif)
				l.unbind_s()

			# in case there is no exception in the above, send the user to a welcome site
			return render_to_response('welcome.html', {
					'username': username,
					'eclass_username': eclass_username,
					'dionysos_username': dionysos_username,
					'webmail_username': webmail_username,
					'first_name': first_name,
					'last_name': last_name,
					'semester': semester,
					'school': school,
					'introduction_year': introduction_year,
					'registration_number': registration_number,
				}, context_instance = RequestContext(request))
		except:
			if msg == '':
				msg = 'Παρουσιάστηκε Σφάλμα'
			return self.render(self.get_form(0), request, 0, context = {
					'msg': msg,
				})

	def get_template(self, step):
		return settings.PROJECT_ROOT + 'templates/signup.html'
