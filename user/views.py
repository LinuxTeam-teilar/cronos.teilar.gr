# -*- coding: utf-8 -*-

from cronos.announcements.models import Id
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

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
	other_list = []
	other_list.append(['noc', 'teilar', 'career', 'linuxteam', 'school', 'pr', 'dionysos', 'library'])
	other_list.append(['cid50', 'cid0', 'cid51', 'cid52', request.user.get_profile().school, 'cid55', 'cid53', 'cid54'])
	other_list.append([])
	i = 0
	form_other = []
	for item in Id.objects.filter(urlid__in = other_list[1]).order_by('name'):
		try:
			if other_list[1][i] in request.user.get_profile().other_announcements.split(','):
				other_list[2].append('checked="yes"')
			else:
				other_list[2].append('')
		except:
			other_list[2].append('')
			pass
		form_other.append('<input type="checkbox" name="' + other_list[0][i] + '" id="id_' + other_list[0][i] + '" ' + other_list[2][i] + \
							' /><label for="id_' + other_list[0][i] + '">' + item.name + '</label>')
		i += 1

	form_teacher = []
	i = 0
	for item in Id.objects.filter(urlid__startswith='pid').order_by('name'):
		try:
			if item.urlid in request.user.get_profile().teacher_announcements.split(','):
				checked = 'checked="yes"'
			else:
				checked = ''
		except:
			checked = ''
			pass
		form_teacher.append('<input type="checkbox" name="' + item.urlid + '" id="id_' + item.urlid + '" ' + checked + \
							' /><label for="id_' + item.urlid + '">' + item.name + '</label>')
		i += 1
	msg = ''
	'''if request.method == 'POST':
		form = OtherAnnouncements(request.POST)
		
		msg = 'Η αλλαγή ήταν επιτυχής'
	else:
		form = OtherAnnouncements()'''
	return render_to_response('settings.html', {
			'school': getschool(request),
			'mail': getmail(request),
			#'form': form,
			'msg': msg,
			'form_other': form_other,
			'form_teacher': form_teacher,
		}, context_instance = RequestContext(request))
