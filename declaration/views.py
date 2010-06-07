# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def declaration(request):
	declaration_full = request.user.get_profile().declaration.split(',')
	i = 3
	summary = declaration_full[:i]
	declaration_lessons = []
	while i <= len(declaration_full):
		declaration_lessons.append(declaration_full[i:i+6])
		i += 6
	print declaration_lessons
	return  render_to_response('declaration.html', {
			'summary': summary,
			'declaration_lessons': declaration_lessons,
		}, context_instance = RequestContext(request))
