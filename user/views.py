# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from cronos.announcements.models import Id

def getmail(request):
	if request.user.email[-21:] == 'notapplicablemail.com':
		mail = 'unset'
	elif request.user.get_profile().webmail_username:
		mail = request.user.get_profile().webmail_username + '@teilar.gr'
	else:
		''
	return mail

def getschool(request):
	for item in Id.objects.filter(urlid__exact = request.user.get_profile().school):
		school = str(item.name)
	return school

@login_required
def user(request):
	return render_to_response('user.html', {
			'mail': getmail(request),
		}, context_instance = RequestContext(request))

@login_required
def user_settings(request):
	return render_to_response('settings.html', {
			'school': getschool(request),
			'mail': getmail(request),
		}, context_instance = RequestContext(request))
