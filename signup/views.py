# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.signup.forms import *
from cronos.announcements.models import Id
from cronos.login.encryption import sha1Password, encryptPassword, decryptPassword
from cronos.login.teilar import *
from cronos.user.update import *
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard

class SignupWizard(FormWizard):
	def done(self, request, form_list):
		msg = ''
		dionysos_username = str([form.cleaned_data for form in form_list][0]['dionysos_username'])
		dionysos_password = encryptPassword(str([form.cleaned_data for form in form_list][0]['dionysos_password']))
		eclass_username = str([form.cleaned_data for form in form_list][1]['eclass_username'])
		if eclass_username:
			eclass_password = encryptPassword(str([form.cleaned_data for form in form_list][1]['eclass_password']))
		else:
			eclass_username = ''
		webmail_username = str([form.cleaned_data for form in form_list][2]['webmail_username'])
		if webmail_username:
			webmail_password = encryptPassword(str([form.cleaned_data for form in form_list][2]['webmail_password']))
		else:
			webmail_username = ''
		username = str([form.cleaned_data for form in form_list][3]['username'])
		password1 = str([form.cleaned_data for form in form_list][3]['password1'])
		password2 = str([form.cleaned_data for form in form_list][3]['password2'])
		try:
			if password1 != password2:
				msg = 'Οι κωδικοί δεν ταιριάζουν'
				raise
			else:
				password = sha1Password(password1)
			output = dionysos_login(0, dionysos_username, decryptPassword(dionysos_password))
			if output == 1:
				msg = 'Λάθος Στοιχεία dionysos'
				raise
			soup = BeautifulSoup(output)
			soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
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
			link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
			output = dionysos_login(link, dionysos_username, decryptPassword(dionysos_password))
			declaration = declaration_update(output)
			link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
			output = dionysos_login(link, dionysos_username, decryptPassword(dionysos_password))
			grades = grades_update(output)

			# login to eclass
			if eclass_username:
				output = eclass_login(eclass_username, decryptPassword(eclass_password))
				if output == 1:
					msg = 'Λάθος Στοιχεία e-class'
					raise
				eclass_lessons = eclass_lessons_update(output)

			# login to webmail
			if webmail_username:
				output = webmail_login(0, webmail_username, decryptPassword(webmail_password))
				if output == 1:
					msg = 'Λάθος Στοιχεία webmail'
					raise

			# add to ldap
			from django.conf import settings
			import ldap
			import ldap.modlist as modlist
			
			l=ldap.initialize(settings.LDAP_URL)
			l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
	
			# before adding to ldap, check if user is already there
			try:
				if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'uid=%s' % (username),settings.SEARCH_FIELDS):
					msg = 'Το username υπάρχει ήδη'
					raise
				if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'registrationNumber=%s' % (registration_number),settings.SEARCH_FIELDS):
					msg = 'Ο χρήστης υπάρχει ήδη'
					raise
				if eclass_username:
					if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'eclassUsername=%s' % (eclass_username),settings.SEARCH_FIELDS):
						msg = 'Το eclass υπάρχει ήδη'
						raise
				if webmail_username:
					if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'webmailUsername=%s' % (webmail_username),settings.SEARCH_FIELDS):
						msg = 'Το webmail υπάρχει ήδη'
						raise
			except:
				pass
				
			attrs = {}
			attrs['objectClass'] = ['person', 'top', 'teilarStudent', 'posixAccount']
			attrs['uid'] =  [username]
			attrs['sn'] = [last_name]
			attrs['cn'] = [first_name]
			attrs['userPassword'] = [password]
			# add cid instead of full name in school attr
			for item in Id.objects.filter(name__exact = (school)):
				cid = str(item.urlid)
			attrs['school'] = [cid]
			attrs['semester'] = [semester]
			attrs['introductionYear'] = [introduction_year]
			attrs['registrationNumber'] = [registration_number]
			attrs['dionysosUsername'] = [dionysos_username]
			attrs['dionysosPassword'] = [dionysos_password]
			if declaration:
				attrs['declaration'] = []
				for item in declaration:
					attrs['declaration'].append(','.join(item))
			if grades:
				attrs['grades'] = []
				for item in grades:
					attrs['grades'].append(','.join(item))
			if eclass_username:
				attrs['eclassUsername'] = [eclass_username]
				attrs['eclassPassword'] = [eclass_password]
				if eclass_lessons:
					attrs['eclassLessons'] = eclass_lessons
			if webmail_username:
				attrs['webmailUsername'] = [webmail_username]
				attrs['webmailPassword'] = [webmail_password]
				attrs['cronosEmail'] = [webmail_username + '@teilar.gr']
			else:
				attrs['cronosEmail'] = [username + '@emptymail.com']
			attrs['homeDirectory'] = ['/home/' + username]
			attrs['gidNumber'] = ['100'] # 100 is the users group in linux
			try:
				results = l.search_s(settings.SEARCH_DN, ldap.SCOPE_SUBTREE, 'uid=*', ['uidNumber'])
				uids = []
				for item in results:
					uids.append(int(item[1]['uidNumber'][0]))
				attrs['uidNumber'] = [str(max(uids) + 1)]
			except:
				attrs['uidNumber'] = ['0']
				# ldap is empty, initializing it
				init_attrs1 = {}
				init_attrs1['objectClass'] = ['dcObject', 'organizationalUnit', 'top']
				init_attrs1['dc'] = ['teilar']
				init_attrs1['ou'] = ['TEI Larissas']
				ldif1 = modlist.addModlist(init_attrs1)
				l.add_s('dc=teilar,dc=gr', ldif1)

				init_attrs2 = {}
				init_attrs2['objectClass'] = ['organizationalUnit', 'top']
				init_attrs2['ou'] = ['teilarStudents']
				ldif2 = modlist.addModlist(init_attrs2)
				l.add_s('ou=teilarStudents,dc=teilar,dc=gr', ldif2)

			ldif = modlist.addModlist(attrs)
			l.add_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (username), ldif)
			l.unbind_s()

			# notify the admins about the new user
			try:
				from django.core.mail import send_mail

				send_mail(
					'Cronos user No.%s: %s' % (str(max(uids) + 2)[2:], username), 
					'Name: %s %s \nDepartment: %s\nSemester: %s' % (first_name, last_name, school, semester),
					'signup@cronos.teilar.gr',
					['cronos@teilar.gr']
				)
			except:
				pass

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
		except ImportError:
			if msg == '':
				msg = 'Παρουσιάστηκε Σφάλμα'
			return self.render(self.get_form(0), request, 0, context = {
					'msg': msg,
				})

	def get_template(self, step):
		return settings.PROJECT_ROOT + 'templates/signup.html'
