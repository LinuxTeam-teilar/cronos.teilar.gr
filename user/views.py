# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.libraries.encryption import sha1Password, encryptPassword, decryptPassword
from cronos.libraries.login import *
from cronos.user.forms import *
from cronos.user.update import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext


def getmail(request):
	if request.user.email[-13:] == 'emptymail.com':
		mail = ''
	else:
		mail = request.user.email
	return mail

def getschool(request):
	for item in Id.objects.filter(urlid__exact = request.user.get_profile().school):
		school = item.name
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
					output = dionysos_login(0, request.POST.get('dionysos_username'), request.POST.get('dionysos_password'))
					if output != 1:
						soup = BeautifulSoup(output)
						soup1 = BeautifulSoup(str(soup.findAll('table')[13]))
						soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
						registration_number = str(soup2.findAll('td')[1].contents[0])
						if registration_number != request.user.get_profile().registration_number:
							msg = 'Οι Αριθμοί Μητρώου δεν ταιριάζουν'
							raise
						user = UserProfile.objects.get(user__username = request.user.username)
						user.dionysos_username = request.POST.get('dionysos_username')
						user.dionysos_password = encryptPassword(request.POST.get('dionysos_password'))
						user.save()

						msg = 'Η ανανέωση των στοιχείων για το dionysos ήταν επιτυχής'
					else:
						msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το dionysos'
				except:
					if not msg:
						msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('eclass_username'):
			eclass1_form = Eclass1Form(request.POST)
			if eclass1_form.is_valid():
				try:
					output = eclass_login(request.POST.get('eclass_username'), request.POST.get('eclass_password'))
					if output != 1:
						if result and result[0][1]['eclassUsername'][0] != request.user.get_profile().eclass_username:
							msg = 'Ο χρήστης eclass υπάρχει ήδη'
							raise
						eclass_lessons = eclass_lessons_update(output)
						user = UserProfile.objects.get(user__username = request.user.username)
						user.eclass_username = request.POST.get('eclass_username')
						user.eclass_password = encryptPassword(request.POST.get('eclass_password'))
						user.eclass_lessons = ','.join(eclass_lessons)
						user.save()
					
						msg = 'Η ανανέωση των στοιχείων για το e-class ήταν επιτυχής'
					else:
						msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το e-class'
				except:
					if not msg:
							msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('webmail_username'):
			webmail_form = WebmailForm(request.POST)
			if webmail_form.is_valid():
				try:
					output = webmail_login(0, request.POST.get('webmail_username'), request.POST.get('webmail_password'))
					if output != 1:
						if result and result[0][1]['webmailUsername'][0] != request.user.get_profile().webmail_username:
							msg = 'Ο χρήστης webmail υπάρχει ήδη'
							raise
						user = UserProfile.objects.get(user__username = request.user.username)
						user.webmail_username = request.POST.get('webmail_username')
						user.webmail_password = encryptPassword(request.POST.get('webmail_password'))
						user.save()
					
						msg = 'Η ανανέωση των στοιχείων για το webmail ήταν επιτυχής'
					else:
						msg = 'Τα στοιχεία δεν επαληθεύτηκαν από το webmail'
				except:
					if not msg:
						msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('email'):
			email_form = EmailForm(request.POST)
			if email_form.is_valid():
				try:
					user = User.objects.get(username = request.user.username)
					user.email = request.POST.get('email')
					user.save()

					msg = 'Η ανανέωση του email σας ήταν επιτυχής'
				except:
					msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST) == str('<QueryDict: {u\'declaration\': [u\'\']}>'):
			declaration_form = DeclarationForm(request.POST)
			try:
				link = 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
				output = dionysos_login(link, request.user.get_profile().dionysos_username, decryptPassword(request.user.get_profile().dionysos_password))
				declaration = declaration_update(output)
				if declaration:
					user = UserProfile.objects.get(user__username = request.user.username)
					temp = []
					for item in declaration:
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
			try:
				link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
				output = dionysos_login(link, request.user.get_profile().dionysos_username, decryptPassword(request.user.get_profile().dionysos_password))
				grades = grades_update(output)
				if grades:
					user = UserProfile.objects.get(user__username = request.user.username)
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
			try:
				output = eclass_login(request.user.get_profile().eclass_username, decryptPassword(request.user.get_profile().dionysos_password))
				eclass_lessons = eclass_lessons_update(output)
				user = UserProfile.objects.get(user__username = request.user.username)
				user.eclass_lessons = ','.join(eclass_lessons)
				user.save()
				msg = 'Η ανανέωση των μαθημάτων του e-class ήταν επιτυχής'
			except:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST)[:34] == '<QueryDict: {u\'teacherann_selected':
			try:
				user = UserProfile.objects.get(user__username = request.user.username)
				user.teacher_announcements = ','.join(request.POST.getlist('teacherann_selected'))
				user.save()
				msg = 'Η ανανέωση πραγματοποιήθηκε με επιτυχία'
			except ImportError:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if str(request.POST)[:32] == '<QueryDict: {u\'otherann_selected':
			try:
				user = UserProfile.objects.get(user__username = request.user.username)
				user.other_announcements = ','.join(request.POST.getlist('otherann_selected'))
				user.save()
				msg = 'Η ανανέωση πραγματοποιήθηκε με επιτυχία'
			except ImportError:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('delete1'):
			try:
				user = UserProfile.objects.get(user__username = request.user.username)
				user.teacher_announcements = ''
				user.save()
				msg = 'Η διαγραφή πραγματοποιήθηκε με επιτυχία'
			except ImportError:
				msg = 'Παρουσιάστηκε Σφάλμα'
		if request.POST.get('delete2'):
			try:
				user = UserProfile.objects.get(user__username = request.user.username)
				user.other_announcements = ''
				user.save()
				msg = 'Η διαγραφή πραγματοποιήθηκε με επιτυχία'
			except ImportError:
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
	
	teacher_announcements_selected = []
	try:
		for teacher in Id.objects.filter(urlid__in = request.user.get_profile().teacher_announcements.split(',')).order_by('name'):
			teacher_announcements_selected.append([teacher.urlid, teacher.name])
	except:
		pass
	
	teacher_announcements_all = []
	teachers = Id.objects.filter(urlid__startswith = 'pid').order_by('name')
	if request.user.get_profile().teacher_announcements:
		teachers = teachers.exclude(urlid__in = request.user.get_profile().teacher_announcements.split(','))
	for teacher in teachers:
			teacher_announcements_all.append([teacher.urlid, teacher.name])

	other_announcements_selected = []
	try:
		for item in Id.objects.filter(urlid__in = request.user.get_profile().other_announcements.split(',')).order_by('name'):
			other_announcements_selected.append([item.urlid, item.name])
	except:
		pass
	
	other_announcements_all = []
	others = Id.objects.filter(Q(urlid__startswith = 'cid5') | Q(urlid__exact = 'cid0')).order_by('name')
	if request.user.get_profile().other_announcements:
		others = others.exclude(urlid__in = request.user.get_profile().other_announcements.split(','))
	for item in others:
			other_announcements_all.append([item.urlid, item.name])

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
			'teacher_announcements_all': teacher_announcements_all,
			'teacher_announcements_selected': teacher_announcements_selected,
			'other_announcements_all': other_announcements_all,
			'other_announcements_selected': other_announcements_selected,
			'msg': msg,
		}, context_instance = RequestContext(request))
