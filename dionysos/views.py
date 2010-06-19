# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.dionysos.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def dionysos(request):
	msg = ''
	summary = ''
	declaration_lessons = []
	if request.user.get_profile().declaration:
		declaration_full = request.user.get_profile().declaration.split(',')
		i = 3
		summary = declaration_full[:i]
		while i <= len(declaration_full) - len(summary):
			declaration_lessons.append(declaration_full[i:i+6])
			i += 6
	else:
		msg = 'Η δήλωσή σας είναι κενή'

	grades = []
	if request.user.get_profile().grades:
		grades_full = request.user.get_profile().grades.split(',')
		length = len(grades_full)
		i = 0
		while i < length - 6:
			if grades_full[i][:7] == 'Εξάμηνο':
				grades.append([str(grades_full[i])])
				i += 1
			elif str(grades_full[i+5])[:5] == 'total':
				grades.append([
					str(grades_full[i]),
					str(grades_full[i+1]),
					#str(grades_full[i+2]),
					str(grades_full[i+3]),
					#str(grades_full[i+4]),
				])
				i += 6 
			else: 
				grades.append([
					str(grades_full[i]),
					#str(grades_full[i+1]),
					#str(grades_full[i+2]),
					str(grades_full[i+3]),
					str(grades_full[i+4]),
					#str(grades_full[i+5]),
					str(grades_full[i+6]),
				])
				i += 7
		total = [
			str(grades_full[i]),
			str(grades_full[i+1]),
			#str(grades_full[i+2]),
			str(grades_full[i+3]),
			#str(grades_full[i+4]),
		]
	return  render_to_response('dionysos.html', {
			'summary': summary,
			'declaration_lessons': declaration_lessons,
			'grades': grades,
			'total': total,
			'msg': msg,
		}, context_instance = RequestContext(request))
