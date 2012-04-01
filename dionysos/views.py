# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.dionysos.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def dionysos(request):
    summary = ''
    total = ''
    declaration_lessons = []
    if request.user.get_profile().declaration:
        declaration_full = request.user.get_profile().declaration.split(',')
        i = 0
        print len(declaration_full)
        while i <= len(declaration_full):
            declaration_lessons.append(declaration_full[i:i+6])
            i += 6

    grades = []
    '''
    if request.user.get_profile().grades:
        grades_full = request.user.get_profile().grades.split(',')
        length = len(grades_full)
        i = 0
        while i < length - 6:
            if grades_full[i][:7] == u'Εξάμηνο':
                grades.append([grades_full[i]])
                i += 1
            elif grades_full[i+5][:5] == 'total':
                grades.append([
                    str(grades_full[i]),
                    str(grades_full[i+1]),
                    #str(grades_full[i+2]),
                    grades_full[i+3],
                    #str(grades_full[i+4]),
                ])
                i += 6 
            else: 
                grades.append([
                    grades_full[i],
                    #str(grades_full[i+1]),
                    #str(grades_full[i+2]),
                    grades_full[i+3],
                    #str(grades_full[i+4]),
                    grades_full[i+5],
                    grades_full[i+6],
                ])
                i += 7
        total = [
            grades_full[i],
            grades_full[i+1],
            #str(grades_full[i+2]),
            grades_full[i+3],
            #str(grades_full[i+4]),
        ]'''
    print declaration_lessons
    return  render_to_response('dionysos.html', {
            'summary': summary,
            'declaration_lessons': declaration_lessons,
            'grades': grades,
            'total': total,
        }, context_instance = RequestContext(request))
