# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.signup.forms import *
from cronos.announcements.models import Id
from cronos.login.encryption import sha1Password, encryptPassword, decryptPassword
from cronos.login.teilar import *
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
				link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
				output = dionysos_login(link, dionysos_username, decryptPassword(dionysos_password))
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
				output = eclass_login(eclass_username, decryptPassword(eclass_password))
				if output == 1:
					msg = 'Λάθος Στοιχεία e-class'
					raise
				soup = BeautifulSoup(output).find('table', 'FormData')
				i = 0
				eclass_lessons = []
				for item in soup.findAll('a'):
					if (i % 2 == 0):
						eclass_lessons.append(str(item.contents[0]).split('-')[0].strip())
					i += 1

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
			if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'uid=%s' % (username),settings.SEARCH_FIELDS) or \
				l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'registrationNumber=%s' % (registration_number),settings.SEARCH_FIELDS):
				msg = 'Ο χρήστης υπάρχει ήδη'
				raise
				
			attrs = {}
			attrs['objectClass'] = ['person','top','teilarStudent', 'posixAccount']
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
				for i in xrange(len(declaration)):
					attrs['declaration'].append(','.join(declaration[i]))
			if eclass_username:
				attrs['eclassUsername'] = [eclass_username]
				attrs['eclassPassword'] = [eclass_password]
				attrs['eclassLessons'] = eclass_lessons
			if webmail_username:
				attrs['webmailUsername'] = [webmail_username]
				attrs['webmailPassword'] = [webmail_password]
				attrs['cronosEmail'] = [webmail_username + '@teilar.gr']
			else:
				attrs['cronosEmail'] = [username + '@emptymail.com']
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
			from django.core.mail import send_mail

			send_mail(
					'Cronos user No. %s: %s' % (str(int(uidNumber[1:]) + 1), username), 
					'Name: %s %s \n Department: %s' % (first_name, last_name, school),
					'signup@cronos.teilar.gr',
					['cs1387@teilar.gr', 'cs1105@teilar.gr', 'tampakrap@gmail.com']
			)

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
