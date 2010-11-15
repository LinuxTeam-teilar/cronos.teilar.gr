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
from django.core.mail import send_mail
import datetime
import ldap
import ldap.modlist as modlist
import os


class MyError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def notifyAdmin(title, message):
	try:
		send_mail(title, message, 'notifications@cronos.teilar.gr', ['cronos@teilar.gr'])
	except:
		pass


def logSignup(error):
	date = datetime.datetime.now()
	date = '%s/%s/%s - %s:%s:%s' % (date.year, date.month, date.day, date.hour, date.minute, date.second)
	try:
		os.mkdir(settings.LOGDIR)
	except OSError as e:
		if e[0] != 17:
			notifyAdmin('mkdir ERROR', e)
			pass
		else:
			pass
	try:
		f = open('%s/signup.log' % (settings.LOGDIR), 'a')
		f.write(' %s || %s ' % (date, error))
		f.close()
	except IOError as e:
		notifyAdmin('log error', e)
		pass


def checkDionysos(credentials):
	output = dionysos_login(0, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
	if output == 1:
		raise MyError('Λάθος Στοιχεία dionysos')
	soup = BeautifulSoup(output)
	try:
		soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[5]))
		credentials['last_name'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Επωνύμου')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[6]))
		credentials['first_name'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Ονόματος')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
		credentials['registration_number'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης ΑΜ')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[9]))
		credentials['semester'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Εξαμήνου')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[8]))
		credentials['school'] = str(soup2.findAll('td')[1].contents[0]).strip()
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Σχολής')
	try:
		soup2 = BeautifulSoup(str(soup.findAll('table')[15]))
		# introduction year is in type first_year - next_year season
		# if season is 'Εαρινό' we parse the second_year, else the first_year
		season = str(soup2.findAll('span','tablecell')[1].contents[0])[:2]
		if season == 'Ε':
			year = str(soup2.findAll('span','tablecell')[0].contents[0].split('-')[1])
		else:
			year = str(soup2.findAll('span','tablecell')[0].contents[0].split('-')[0])
		credentials['introduction_year'] = year + season
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Ε/Α')
	try:
		link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
		output = dionysos_login(link, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
		credentials['declaration'] = declaration_update(output)
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Δήλωσης')
	try:
		link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
		output = dionysos_login(link, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
		credential['grades'] = grades_update(output)
	except Exception as error:
		logSignup(error)
		raise MyError('Αδυναμία ανάκτησης Βαθμολογίας')

def checkEclass(credentials):
	output = eclass_login(credentials['eclass_username'], decryptPassword(credentials['eclass_password']))
	if output == 1:
		raise MyError('Λάθος Στοιχεία e-class')
	credentials['eclass_lessons'] = eclass_lessons_update(output)
		
def checkWebmail(credentials):
	output = webmail_login(0, credentials['webmail_username'], decryptPassword(credentials['webmail_password']))
	if output == 1:
		raise MyError('Λάθος Στοιχεία webmail')

def checkLDAPData(credentials):	
	try:
		l=ldap.initialize(settings.LDAP_URL)
		l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
	except Exception as error:
		logSignup(error)
		raise MyError('Απέτυχε η σύνδεση με τον LDAP')

	# before adding to ldap, check if user is already there

	if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'uid=%s' % (credentials['username']),settings.SEARCH_FIELDS):
		raise MyError('Το username υπάρχει ήδη')
	if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'registrationNumber=%s' % (credentials['registration_number']),settings.SEARCH_FIELDS):
		raise MyError('Ο ΑΜ υπάρχει ήδη')
	if credentials['eclass_username']:
		if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'eclassUsername=%s' % (credentials['eclass_username']),settings.SEARCH_FIELDS):
			raise MyError('Το eclass υπάρχει ήδη')
	if credentials['webmail_username']:
		if l.search_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,'webmailUsername=%s' % (credentials['webmail_username']),settings.SEARCH_FIELDS):
			raise MyError('Το webmail υπάρχει ήδη')

def allDataToLDAP(credentials):
	attrs = {}
	attrs['objectClass'] = ['person', 'top', 'teilarStudent', 'posixAccount']
	attrs['uid'] =  [credentials['username']]
	attrs['sn'] = [credentials['last_name']]
	attrs['cn'] = [credentials['first_name']]
	attrs['userPassword'] = [credentials['password']]
	# add cid instead of full name in school attr
	for item in Id.objects.filter(name__exact = (credentials['school'])):
		cid = str(item.urlid)
	attrs['school'] = [cid]
	attrs['semester'] = [credentials['semester']]
	attrs['introductionYear'] = [credentials['introduction_year']]
	attrs['registrationNumber'] = [credentials['registration_number']]
	attrs['dionysosUsername'] = [credentials['dionysos_username']]
	attrs['dionysosPassword'] = [credentials['dionysos_password']]
	if credentials['declaration']:
		attrs['declaration'] = []
		for item in credentials['declaration']:
			attrs['declaration'].append(','.join(item))
	try:
		attrs['grades'] = []
		for item in credentials['grades']:
			attrs['grades'].append(','.join(item))
	except KeyError:
		pass
	if credentials['eclass_username']:
		attrs['eclassUsername'] = [credentials['eclass_username']]
		attrs['eclassPassword'] = [credentials['eclass_password']]
	if credentials['eclass_lessons']:
		attrs['eclassLessons'] = credentials['eclass_lessons']
	if credentials['webmail_username']:
		attrs['webmailUsername'] = [credentials['webmail_username']]
		attrs['webmailPassword'] = [credentials['webmail_password']]
		attrs['cronosEmail'] = [credentials['webmail_username'] + '@teilar.gr']
	else:
		attrs['cronosEmail'] = [credentials['username'] + '@emptymail.com']
		attrs['(title,messagehomeDirectory'] = ['/home/' + credentials['username']]
		attrs['gidNumber'] = ['100'] # 100 is the users group in linux
	try:
		results = l.search_s(settings.SEARCH_DN, ldap.SCOPE_SUBTREE, 'uid=*', ['uidNumber'])
		uids = []
		for item in results:
			uids.append(int(item[1]['uidNumber'][0]))
			attrs['uidNumber'] = [str(max(uids) + 1)]
	except:
		attrs['uidNumber'] = ['1']
		# ldap is empty, initializing it
		init_attrs1 = {}
		init_attrs1['objectClass'] = ['dcObject', 'organizationalUnit', 'top']
		init_attrs1['dc'] = ['teilar']
		init_attrs1['ou'] = ['TEI Larissas']
		ldif1 = modlist.addModlist(init_attrs1)
		try:
			l.add_s('dc=teilar,dc=gr', ldif1)
		except Exception as error:
			logSignup(error)
			raise MyError('Αποτυχία Εισαγωγής Στοιχείων')
		init_attrs2 = {}
		init_attrs2['objectClass'] = ['organizationalUnit', 'top']
		init_attrs2['ou'] = ['teilarStudents']
		ldif2 = modlist.addModlist(init_attrs2)
		try:
			l.add_s('ou=teilarStudents,dc=teilar,dc=gr', ldif2)
		except Exception as error:
			logSignup(error)
			raise MyError('Αποτυχία Εισαγωγής Στοιχείων')

	ldif = modlist.addModlist(attrs)
	try:
		l.add_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (credentials['username']), ldif)
		return attrs['uidNumber']
	except Exception as error:
		logSignup(error)
		raise MyError('Αποτυχία Εισαγωγής Στοιχείων')
	l.unbind_s()

def sendToTemplate(request, credentials, uid):
	title = 'Cronos user No.%s: %s' % (uid, credentials['username'])
	message = 'Name: %s %s \nDepartment: %s\nSemester: %s' % (credentials['first_name'], credentials['last_name'], credentials['school'], credentials['semester'])
	notifyAdmin(title, message)

	return render_to_response('welcome.html', {
		'username': credentials['username'],
		'eclass_username': credentials['eclass_username'],
		'dionysos_username': credentials['dionysos_username'],
		'webmail_username': credentials['webmail_username'],
		'first_name': credentials['first_name'],
		'last_name': credentials['last_name'],
		'semester': credentials['semester'],
		'school': credentials['school'],
		'introduction_year': credentials['introduction_year'],
		'registration_number': credentials['registration_number'],
	}, context_instance = RequestContext(request))

class SignupWizard(FormWizard):
	def collectCredentials(self, request, form_list):
		credentials = {}
		credentials['dionysos_username'] = str([form.cleaned_data for form in form_list][0]['dionysos_username'])
		credentials['dionysos_password'] = encryptPassword(str([form.cleaned_data for form in form_list][0]['dionysos_password']))
		temp = str([form.cleaned_data for form in form_list][1]['eclass_username'])
		if temp:
			credentials['eclass_username'] = temp
			credentials['eclass_password'] = encryptPassword(str([form.cleaned_data for form in form_list][1]['eclass_password']))
		temp = str([form.cleaned_data for form in form_list][2]['webmail_username'])
		if temp:
			credentials['webmail_username'] = temp
			credentials['webmail_password'] = encryptPassword(str([form.cleaned_data for form in form_list][2]['webmail_password']))
		# check passwords
		password1 = str([form.cleaned_data for form in form_list][3]['password1'])
		password2 = str([form.cleaned_data for form in form_list][3]['password2'])
		if password1 == password2:
			credentials['password'] = sha1Password(password1)
			credentials['username'] = str([form.cleaned_data for form in form_list][3]['username'])
			return credentials
		else:
			raise MyError('Οι κωδικοί δεν ταιριάζουν')

	def sendErrorTemplate(self, request, form_list, msg):
		return self.render(self.get_form(0), request, 0, context = {
				'msg': msg,
			})

	def done(self, request, form_list):
	# in case there is no exception in the above, send the user to a welcome site
		uid = ''
		try:
			credentials = self.collectCredentials(request, form_list)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		try:
			checkDionysos(credentials)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		try:
			checkEclass(credentials)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		try:
			checkWebmail(credentials)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		try:
			checkLDAPData(credentials)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		try:
			uid = allDataToLDAP(credentials)
		except MyError as e:
			self.sendErrorTemplate(request, form_list, e.value)
		sendToTemplate(request, credentials, uid)

	def get_template(self, step):
		return settings.PROJECT_ROOT + 'templates/signup.html'
