# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
#from django.contrib.auth.models import User
#from django.contrib.auth import authenticate
from cronos.backends.ldapBackend import LDAPBackend

a = LDAPBackend()

b = a.authenticate('Chatzimichos', '123456')


def main(request) :
	template = get_template('main.html')
	variables = Context({
		'head_title': b,
	})
	output = template.render(variables)
	return HttpResponse(output)
