# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

from django.contrib import auth


def main(request) :
	if request.method == "POST":
		post = request.POST.copy()
		if post.has_key('username') and post.has_key('password'):
			usr = post['username']
			pwd = post['password']
			user = auth.authenticate(username=usr, password=pwd)
			if user is not None and user.is_active:
				auth.login(request, user)	
				template = get_template('main.html')
				variables = Context({
					'head_title': 'Αρχική | ',
				})
				output = template.render(variables)
				return HttpResponse(output)
			else:
				template = get_template('login.html')
				variables = Context({
					'head_title': 'Είσοδος | ',
					'msg': 'malakia',
				})
				output = template.render(variables)
				return HttpResponse(output)
	if request.user.is_authenticated():
		return render_to_response("main.html", {'head_title': 'Αρχική | '})
	else:
		return render_to_response("login.html", {'head_title': 'Είσοδος | '})
