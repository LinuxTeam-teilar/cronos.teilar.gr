# -*- coding: utf-8 -*-

from apps.teilar.models import Teachers
from django.shortcuts import render_to_response
from django.template import RequestContext

def teachers(request):
    teachers_list = []
    for item in Teachers.objects.filter(deprecated = False).order_by('name'):
        teachers_list.append([item.name, item.email, item.department])
    return render_to_response('teachers.html', {
            'teachers': teachers_list,
        }, context_instance = RequestContext(request))
