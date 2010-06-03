# -*- coding: utf-8 -*-

from cronos.login.forms import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login, authenticate, logout

def mylogin(request):
	msg = ''
	form = ''
	if request.method == "POST":
		form = LoginForm(request.POST)
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username = username, password = password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/user')
		else:
			msg = 'Λάθος Κωδικός'
	else:
		if request.user.is_authenticated():
			return HttpResponseRedirect('/user')
		else:
			form = LoginForm()
	return render_to_response('login.html', {
			'head_title': 'Είσοδος | ',
			'msg': msg,
			'form': form,
		}, context_instance = RequestContext(request))

def mylogout(request):
	logout(request)
	return HttpResponseRedirect('/')

#todo
#def about(request):
#
