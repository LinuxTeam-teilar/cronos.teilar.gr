# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
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

def about(request):
	return render_to_response('about.html', {
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
	grades_form = GradesForm()
	eclass2_form = Eclass2Form()
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
				output = dionysos_login(0, request.POST.get('dionysos_username'), request.POST.get('dionysos_password'))
				if output != 1:
					try:
						soup = BeautifulSoup(output)
						soup1 = BeautifulSoup(str(soup.findAll('table')[13]))
						soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
						registration_number = str(soup2.findAll('td')[1].contents[0])
						if registration_number != request.user.get_profile().registration_number:
							msg = 'Οι Αριθμοί Μητρώου δεν ταιριάζουν'
							raise
						l = ldap.initialize(settings.LDAP_URL)
						l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
						mod_attrs = modlist.modifyModlist({'dionysosUsername': [request.user.get_profile().dionysos_username]}, {'dionysosUsername': [str(request.POST.get('dionysos_username'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						mod_attrs = modlist.modifyModlist({'dionysosPassword': [request.user.get_profile().dionysos_password]}, {'dionysosPassword': [encryptPassword(request.POST.get('dionysos_password'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						l.unbind_s()

						user = LdapProfile.objects.get(user__username = request.user.username)
						user.dionysos_username = request.POST.get('dionysos_username')
						user.dionysos_password = encryptPassword(request.POST.get('dionysos_password'))
						user.save()

						msg = 'Η ανανέωση των στοιχείων για το dionysos ήταν επιτυχής'
					except:
						if not msg:
							msg = 'Παρουσιάστηκε Σφάλμα'
				else:
					msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το dionysos'
		if request.POST.get('eclass_username'):
			eclass1_form = Eclass1Form(request.POST)
			if eclass1_form.is_valid():
				output = eclass_login(request.POST.get('eclass_username'), request.POST.get('eclass_password'))
				if output != 1:
					try:
						l = ldap.initialize(settings.LDAP_URL)
						l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
						try:
							result = l.search_s('ou=teilarStudents,dc=teilar,dc=gr', ldap.SCOPE_SUBTREE, 'eclassUsername=%s' % (request.POST.get('eclass_username')), ['*'])
						except:
							result = ''
							pass
						if result and result[0][1]['eclassUsername'][0] != request.user.get_profile().eclass_username:
							msg = 'Ο χρήστης eclass υπάρχει ήδη'
							raise
						mod_attrs = modlist.modifyModlist({'eclassUsername': [request.user.get_profile().eclass_username]}, {'eclassUsername': [str(request.POST.get('eclass_username'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						mod_attrs = modlist.modifyModlist({'eclassPassword': [request.user.get_profile().eclass_password]}, {'eclassPassword': [encryptPassword(request.POST.get('eclass_password'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)

						soup = BeautifulSoup(output).find('table', 'FormData')
						i = 0
						eclass_lessons = []
						for item in soup.findAll('a'):
							if (i % 2 == 0):
								eclass_lessons.append(str(item.contents[0]).split('-')[0].strip())
							i += 1
						try:
							mod_attrs = [(ldap.MOD_DELETE, 'eclassLessons', None)]
							l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						except:
							pass
						mod_attrs = []
						for item in eclass_lessons:
							mod_attrs.append((ldap.MOD_ADD, 'eclassLessons', item))
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						l.unbind_s()

						user = LdapProfile.objects.get(user__username = request.user.username)
						user.eclass_username = request.POST.get('eclass_username')
						user.eclass_password = encryptPassword(request.POST.get('eclass_password'))
						user.eclass_lessons = ','.join(eclass_lessons)
						user.save()
					
						msg = 'Η ανανέωση των στοιχείων για το e-class ήταν επιτυχής'
					except:
						if not msg:
							msg = 'Παρουσιάστηκε Σφάλμα'
				else:
					msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το e-class'
		if request.POST.get('webmail_username'):
			webmail_form = WebmailForm(request.POST)
			if webmail_form.is_valid():
				output = webmail_login(0, request.POST.get('webmail_username'), request.POST.get('webmail_password'))
				if output != 1:
					try:
						l = ldap.initialize(settings.LDAP_URL)
						l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
						try:
							result = l.search_s('ou=teilarStudents,dc=teilar,dc=gr', ldap.SCOPE_SUBTREE, 'webmailUsername=%s' % (request.POST.get('webmail_username')), ['*'])
						except:
							result = ''
							pass
						if result and result[0][1]['webmailUsername'][0] != request.user.get_profile().webmail_username:
							msg = 'Ο χρήστης webmail υπάρχει ήδη'
							raise
						mod_attrs = modlist.modifyModlist({'webmailUsername': [request.user.get_profile().webmail_username]}, {'webmailUsername': [str(request.POST.get('webmail_username'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						mod_attrs = modlist.modifyModlist({'webmailPassword': [request.user.get_profile().webmail_password]}, {'webmailPassword': [encryptPassword(request.POST.get('webmail_password'))]})
						l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
						l.unbind_s()

						user = LdapProfile.objects.get(user__username = request.user.username)
						user.webmail_username = request.POST.get('webmail_username')
						user.webmail_password = encryptPassword(request.POST.get('webmail_password'))
						user.save()
					
						msg = 'Η ανανέωση των στοιχείων για το webmail ήταν επιτυχής'
					except:
						if not msg:
							msg = 'Παρουσιάστηκε Σφάλμα'
				else:
					msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το webmail'
		if request.POST.get('email'):
			email_form = EmailForm(request.POST)
			if email_form.is_valid():
				try:
					l = ldap.initialize(settings.LDAP_URL)
					l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
					mod_attrs = modlist.modifyModlist({'cronosEmail': [getmail(request)]}, {'cronosEmail': [str(request.POST.get('email'))]})
					# skip this step to the end of the procedure, as django user db does a check if the given string is a valid mail
					#l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)

					user = User.objects.get(username = request.user.username)
					user.email = request.POST.get('email')
					user.save()

					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()
					
					msg = 'Η ανανέωση του email σας ήταν επιτυχής'
				except:
					msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST) == str('<QueryDict: {u\'declaration\': [u\'\']}>'):
			declaration_form = DeclarationForm(request.POST)
			link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
			output = dionysos_login(link, request.user.get_profile().dionysos_username, decryptPassword(request.user.get_profile().dionysos_password))
			try:
				soup = BeautifulSoup(output)
				soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
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

				l = ldap.initialize(settings.LDAP_URL)
				l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
				try:
					mod_attrs = [(ldap.MOD_DELETE, 'declaration', None)]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				except:
					pass
	
				if declaration_new:
					mod_attrs = []
					for item in declaration_new:
						mod_attrs.append((ldap.MOD_ADD, 'declaration', ','.join(item)))
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()
				
					user = LdapProfile.objects.get(user__username = request.user.username)
					temp = []
					for item in declaration_new:
						temp += item
					user.declaration = ','.join(temp)
					user.save()
					msg = 'Η ανανέωση της δήλωσής σας ήταν επιτυχής'
				else:
					msg = 'Η δήλωσή σας είναι κενή'
			except:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST) == str('<QueryDict: {u\'grades\': [u\'\']}>'):
			grades_form = GradesForm(request.POST)
			link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
			output = dionysos_login(link, request.user.get_profile().dionysos_username, decryptPassword(request.user.get_profile().dionysos_password))
			try:
				soup = BeautifulSoup(output)
				grades = []
				i = 0
				item = soup.findAll('table')[13].findAll('td')
				length_all_td = len(item)
				semesters = soup.findAll('table')[13].findAll('td', 'groupHeader')
				lessons = soup.findAll('table')[13].findAll('td', 'topBorderLight')
				while i < length_all_td:
					item0 = item[i]
					if item0 in semesters:
						grades.append([str(item0.contents[0])])
					if item0 in lessons:
						year = str(item[i+6].contents[0].i.contents[0]).strip()
						year = year[:10] + year[-9:]
						if year == '--':
							year = '-'
						grades.append([
							str(item0.contents[0]).strip(),
							str(item[i+1].contents[0]).strip(),
							str(item[i+2].contents[0]).strip(),
							str(item[i+3].contents[0]).strip(),
							str(item[i+4].contents[0]).strip(),
							str(item[i+5].span.contents[0]).strip(),
							year,
						])
						try:
							if item[i+9].contents[1][-3:] == '(Θ)' or item[i+9].contents[1][-3:] == '(Ε)':
								year = str(item[i+14].contents[0].i.contents[0]).strip()
								year = year[:10] + year[-9:]
								grades.append([
									str(item[i+9].contents[1]).strip(),
									'',
									str(item[i+10].i.contents[0]).strip(),
									str(item[i+11].contents[0]).strip(),
									str(item[i+12].contents[0]).strip(),
									str(item[i+13].contents[0]).strip(),
									year,
								])
								year = str(item[i+22].contents[0].i.contents[0])
								year = year[:10] + year[-9:]
								grades.append([
									str(item[i+17].contents[i]).strip(),
									'',
									str(item[i+18].i.contents[0]).strip(),
									str(item[i+19].contents[0]).strip(),
									str(item[i+20].contents[0]).strip(),
									str(item[i+21].contents[0]).strip(),
									year,
								])
								i += 11
						except:
							pass
						i += 6
					try:
						if item0.contents[0][:6] == 'Σύνολα':
							grades.append([
								str(item0.b.contents[0]),
								str(item[i+1].contents[1].contents[0]).strip(),
								str(item[i+1].contents[3].contents[0]).strip(),
								str(item[i+1].contents[5].contents[0]).strip(),
								str(item[i+1].contents[7].contents[0]).strip(),
								str(i),
							])
							i += 1
					except:
						pass
					i += 1
				
				general = soup.findAll('table')[13].findAll('tr', 'subHeaderBack')[-1]
				grades.append([
					str(general.b.contents[2][-2:]),
					str(general.contents[1].span.contents[0]),
					str(general.contents[1].b.contents[3].contents[0]),
					str(general.contents[1].b.contents[5].contents[0]),
					str(general.contents[1].b.contents[7].contents[0]),
				])

				l = ldap.initialize(settings.LDAP_URL)
				l.bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
				try:
					mod_attrs = [(ldap.MOD_DELETE, 'grades', None)]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				except:
					pass
	
				if grades:
					mod_attrs = []
					for item in grades:
						mod_attrs.append((ldap.MOD_ADD, 'grades', ','.join(item)))
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
					l.unbind_s()
				
					user = LdapProfile.objects.get(user__username = request.user.username)
					temp = []
					for item in grades:
						temp += item
					user.grades = ','.join(temp)
					user.save()
					msg = 'Η ανανέωση της βαθμολογίας σας ήταν επιτυχής'
				else:
					msg = 'Η βαθμολογία σας είναι κενή'
			except:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST) == str('<QueryDict: {u\'eclass_lessons\': [u\'\']}>'):
			eclass2_form = Eclass2Form(request.POST)
			output = eclass_login(request.user.get_profile().eclass_username, decryptPassword(request.user.get_profile().dionysos_password))
			try:
				l = ldap.initialize(settings.LDAP_URL)
				l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)

				soup = BeautifulSoup(output).find('table', 'FormData')
				i = 0
				eclass_lessons = []
				for item in soup.findAll('a'):
					if (i % 2 == 0):
						eclass_lessons.append(str(item.contents[0]).split('-')[0].strip())
					i += 1
				try:
					mod_attrs = [(ldap.MOD_DELETE, 'eclassLessons', None)]
					l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				except:
					pass
				mod_attrs = []
				for item in eclass_lessons:
					mod_attrs.append((ldap.MOD_ADD, 'eclassLessons', item))
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.user), mod_attrs)
				l.unbind_s()

				user = LdapProfile.objects.get(user__username = request.user.username)
				user.eclass_lessons = ','.join(eclass_lessons)
				user.save()
				msg = 'Η ανανέωση των μαθημάτων του e-class ήταν επιτυχής'
			except:
				msg = 'Παρουσιάστηκε Σφάλμα'

	else:
		cronos_form = CronosForm()
		dionysos_form = DionysosForm()
		eclass1_form = Eclass1Form()
		webmail_form = WebmailForm()
		email_form = EmailForm()
		declaration_form = DeclarationForm()
		grades_form = GradesForm()
		eclass2_form = Eclass2Form()

	return render_to_response('settings.html', {
			'mail': getmail(request),
			'cronos_form': cronos_form,
			'dionysos_form': dionysos_form,
			'eclass1_form': eclass1_form,
			'webmail_form': webmail_form,
			'email_form': email_form,
			'declaration_form': declaration_form,
			'grades_form': grades_form,
			'eclass2_form': eclass2_form,
			'msg': msg,
		}, context_instance = RequestContext(request))
