# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
	
@login_required
def user(request):
	return render_to_response('user.html', {
			'head_title': str(request.user) + ' | ',
		}, context_instance = RequestContext(request))
