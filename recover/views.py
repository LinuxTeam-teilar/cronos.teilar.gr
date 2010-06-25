# -*- coding: utf-8 -*-

from cronos.login.encryption import sha1Password
from cronos.recover import captcha
from cronos.recover.forms import *
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render_to_response
from django.template import RequestContext
from random import choice
import ldap
import string

def recover(request):
	msg = ''
	html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
	if request.method == 'POST':
		print request
		check_captcha = captcha.submit(
			request.POST['recaptcha_challenge_field'],
			request.POST['recaptcha_response_field'],
			settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR']
		)
		form = RecoverForm(request.POST)
		if form.is_valid():
			new_password = ''.join([choice(string.letters + string.digits) for i in range(8)])
			try:
				if check_captcha.is_valid is False:
					msg = 'Το captcha δεν επαληθεύτηκε'
					raise
				try:
					user = User.objects.get(username = request.POST.get('username'))
				except:
					msg = 'Ο χρήστης δεν υπάρχει'
				if not user:
					raise
				
				if user.email[-13:] == 'emptymail.com':
					msg = 'Ο χρήστης δεν έχει δηλώσει email'
					raise

				l = ldap.initialize(settings.LDAP_URL)
				l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
				mod_attrs = [(ldap.MOD_DELETE, 'userPassword', None)]
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.POST.get('username')), mod_attrs)
				mod_attrs = [(ldap.MOD_ADD, 'userPassword', sha1Password(new_password))]
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.POST.get('username')), mod_attrs)
				l.unbind_s()

				user.set_password(new_password)
				user.save()

				send_mail(
					'Νέος Κωδικός για τον χρήστη %s' % (request.POST.get('username')),
					'Ο νέος σας κωδικός είναι %s.\nΗ ομάδα διαχείρισης του Cronos' % (new_password),
					'webmaster@cronos.teilar.gr',
					[user.email]
				)

				msg = 'Το email έχει αποσταλεί'
			except:
				if not msg:
					msg = 'Παρουσιάστηκε σφάλμα'
	else:
		form = RecoverForm()
		html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
	return render_to_response('recover.html', {
			'form': form,
			'html_captcha': html_captcha,
			'msg': msg,
		}, context_instance = RequestContext(request))
