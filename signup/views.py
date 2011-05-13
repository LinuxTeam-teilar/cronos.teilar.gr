# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.signup.forms import *
from cronos.announcements.models import Id
from cronos.libraries.log import CronosError, cronosDebug, mailCronosAdmin
from cronos.login.encryption import sha1Password, encryptPassword, decryptPassword
from cronos.login.teilar import *
from cronos.user.update import *
from cronos.user.models import UserProfile
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template import RequestContext
from django.shortcuts import render_to_response
import datetime
import os

credentials = {
	'username':'',
	'first_name':'',
	'last_name':'',
	'password':'',
	'school':'',
	'semester':'',
	'introduction_year':'',
	'registration_number':'',
	'dionysos_username':'',
	'dionysos_password':'',
	'eclass_username':'',
	'eclass_password':'',
	'eclass_lessons':'',
	'webmail_username':'',
	'webmail_password':'',
}

def checkDionysos():
	global credentials
	output = dionysos_login(0, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
	if output == 1:
		raise CronosError('Λάθος Στοιχεία dionysos')
	soup = BeautifulSoup(output)
	try:
		soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[5]))
		credentials['last_name'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Επωνύμου')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[6]))
		credentials['first_name'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Ονόματος')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
		credentials['registration_number'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης ΑΜ')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[9]))
		credentials['semester'] = str(soup2.findAll('td')[1].contents[0])
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Εξαμήνου')
	try:
		soup2 = BeautifulSoup(str(soup1.findAll('tr')[8]))
		credentials['school'] = str(soup2.findAll('td')[1].contents[0]).strip()
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Σχολής')
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
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Ε/Α')
	try:
		link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
		output = dionysos_login(link, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
		credentials['declaration'] = declaration_update(output)
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Δήλωσης')
	try:
		link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
		output = dionysos_login(link, credentials['dionysos_username'], decryptPassword(credentials['dionysos_password']))
		credentials['grades'] = grades_update(output)
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Αδυναμία ανάκτησης Βαθμολογίας')

def checkEclass():
	global credentials
	output = eclass_login(credentials['eclass_username'], decryptPassword(credentials['eclass_password']))
	if output == 1:
		raise CronosError('Λάθος Στοιχεία e-class')
	credentials['eclass_lessons'] = eclass_lessons_update(output)

def checkWebmail():
	global credentials
	output = webmail_login(0, credentials['webmail_username'], decryptPassword(credentials['webmail_password']))
	if output == 1:
		raise CronosError('Λάθος Στοιχεία webmail')

def collectCredentials(request):
	global credentials
	credentials['dionysos_username'] = str(request.POST.get('dionysos_username'))
	credentials['dionysos_password'] = encryptPassword(str(request.POST.get('dionysos_password')))
	temp = str(request.POST.get('eclass_username'))
	if temp:
		credentials['eclass_username'] = temp
		credentials['eclass_password'] = encryptPassword(str(request.POST.get('eclass_password')))
	temp = str(request.POST.get('webmail_username'))
	if temp:
		credentials['webmail_username'] = temp
		credentials['webmail_password'] = encryptPassword(str(request.POST.get('webmail_password')))
	# check passwords
	password1 = str(request.POST.get('password1'))
	password2 = str(request.POST.get('password2'))
	if password1 == password2:
		credentials['password'] = sha1Password(password1)
		credentials['username'] = str(request.POST.get('username'))
		return credentials
	else:
		raise CronosError('Οι κωδικοί δεν ταιριάζουν')

def addDataToAuthDB():
	user = User(
		username = credentials['username'],
		first_name = credentials['first_name'],
		last_name = credentials['last_name'],
		email = credentials['username'] + '@emptymail.com'
	)
	user.is_staff = False
	user.is_superuser = False
	user.set_password(credentials['password'])
	try:
		user.save()
	except IntegrityError as error:
		# check for duplicate
		if error[0] == 1062:
			raise CronosError('Ο χρήστης υπάρχει ήδη')
		else:
			raise
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Σφάλμα αποθήκευσης χρήστη')

	authStudentProfile = UserProfile(
		user = user,
		dionysos_username = credentials['dionysos_username'],
		dionysos_password = credentials['dionysos_password'],
		eclass_username = credentials['eclass_username'],
		eclass_password = credentials['eclass_password'],
		eclass_lessons = credentials['eclass_lessons'],
		introduction_year = credentials['introduction_year'],
		registration_number = credentials['registration_number'],
		school = credentials['school'],
		semester = credentials['semester'],
		webmail_username = credentials['webmail_username'],
		webmail_password = credentials['webmail_password'],
		declaration = credentials['declaration'],
		grades = credentials['grades'],
	)
	try:
		authStudentProfile.save()
	except Exception as error:
		cronosDebug(error, 'signup.log')
		raise CronosError('Σφάλμα αποθήκευσης χρήστη')

def signup(request):
	global credentials
	uid = ''
	msg = ''
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			try:
				credentials = collectCredentials(request)
				checkDionysos()
				if credentials['eclass_username']:
					checkEclass()
				if credentials['webmail_username']:
					checkWebmail()
				addDataToAuthDB()
				'''title = 'Cronos user No.%s: %s' % (uid, credentials['username'])
				message = 'Name: %s %s \nDepartment: %s\nSemester: %s' % (
						credentials['first_name'],
						credentials['last_name'],
						credentials['school'],
						credentials['semester'])
				mailCronosAdmin(title, message)'''
				return render_to_response('welcome.html', credentials, context_instance = RequestContext(request))
			except CronosError as error:
				msg = error.value
				cronosDebug(msg, 'signup.log') # log the error msg
	else:
		form = SignupForm()
	return render_to_response('signup.html', { 'msg': msg, 'form': form }, context_instance = RequestContext(request))
