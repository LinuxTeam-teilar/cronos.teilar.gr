# -*- coding: utf-8 -*-

from cronos.login.encryption import sha1Password
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
	if request.method == 'POST':
		form = RecoverForm(request.POST)
		if form.is_valid():
			new_password = ''.join([choice(string.letters + string.digits) for i in range(8)])
			try:
				l = ldap.initialize(settings.LDAP_URL)
				l.simple_bind_s(settings.BIND_USER, settings.BIND_PASSWORD)
				mod_attrs = [(ldap.MOD_DELETE, 'userPassword', None)]
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.POST.get('username')), mod_attrs)
				mod_attrs = [(ldap.MOD_ADD, 'userPassword', sha1Password(new_password))]
				l.modify_s('uid=%s,ou=teilarStudents,dc=teilar,dc=gr' % (request.POST.get('username')), mod_attrs)
				l.unbind_s()

				user = User.objects.get(username = request.POST.get('username'))
				user.set_password(new_password)
				user.save()

				send_mail(
					'Νέος Κωδικός για τον χρήστη %s' % (request.POST.get('username')),
					'Ο νέος σας κωδικός είναι %s.\nΗ ομάδα διαχείρισης του Cronos' % (new_password),
					'webmaster@cronos.teilar.gr',
					[user.email]
				)

				msg = 'Το email έχει αποσταλεί'
			except ImportError:
				msg = 'Παρουσιάστηκε σφάλμα'
	else:
		form = RecoverForm()
	return render_to_response('recover.html', {
			'form': form,
			'msg': msg,
		}, context_instance = RequestContext(request))
