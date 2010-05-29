# -*- coding: utf-8 -*-

from cronos.signup.forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			template = get_template('signup.html')
			variables = Context({
				'id': 'set',
				'test': 'test',
			})
			output = template.render(variables)
			return HttpResponse(output)
	else:
		form = SignupForm()
	return render_to_response('signup.html', {'form': form, } )
