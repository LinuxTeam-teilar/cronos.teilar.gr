# -*- coding: utf-8 -*-

from cronos.teilar.forms import LibraryForm
from cronos.teilar.models import Teachers, EclassLessons
from cronos.teilar import teilar_anon_login
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

def teachers(request):
    '''
    The webpage with all the teachers and their emails
    '''
    teachers = Teachers.objects.filter(is_active = True).order_by('name')
    for teacher in teachers:
        teacher.urlid = teacher.url.split('=')[1]
    return render_to_response('teachers.html', {
            'teachers': teachers,
        }, context_instance = RequestContext(request))

def library(request):
    '''
    Perform search in library.teilar.gr and print the results
    '''
    msg = None
    results = []
    if request.method == 'GET':
        form = LibraryForm(request.GET)
        if form.is_valid():
            url = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=40&ipp=20&spp=20&profile=multbl--1&ri=&term=%s&index=.GEN&x=0&y=0&aspect=subtab22' % str(request.GET.get('search'))
            output = teilar_anon_login(url, request)
            soup = BeautifulSoup(output).find_all('table')[24]
            temp_a_mediumboldanchor = soup.find_all('a', 'mediumBoldAnchor')
            temp_td = soup.find_all('td')
            i = 5
            for item in temp_a_mediumboldanchor:
                title = item.contents[0]
                '''
                The authors are in <i> tags. Take the list of them by
                taking a list of the contents of <i> tags, and then
                join the list with commas for prettier output
                '''
                authors = []
                tmp_authors = temp_td[i].find_all('i')
                for author in tmp_authors:
                    authors.append(author.contents[0].replace(',', '').strip())
                authors = ', '.join(authors)
                editor = temp_td[i+1].contents[0].contents[0].split(' : ')[1]
                city = temp_td[i+1].contents[0].contents[0].split(' : ')[0]
                i += 10
                results.append([title, authors, editor, city])
            if not results:
                msg = 'Δεν υπάρχουν αποτελέσματα'
    else:
        form = SearchForm()
    return render_to_response('library.html', {
            'form': form,
            'msg': msg,
            'results': results,
        }, context_instance = RequestContext(request))

@login_required
def dionysos(request):
    '''
    Retrieve the declaration and grades from the DB and print them
    '''

    '''
    Retrieve and print the declaration
    '''
    declaration = []
    if request.user.get_profile().declaration:
        declaration_full = request.user.get_profile().declaration.split(':')
        i = 0
        while i <= len(declaration_full):
            declaration.append(declaration_full[i:i+7])
            i += 7

    '''
    Retrieve and print the grades
    '''
    # TODO
    grades = []
    return  render_to_response('dionysos.html', {
            'declaration': declaration,
            'grades': grades,
        }, context_instance = RequestContext(request))

@login_required
def eclass(request):
    eclass_lessons = EclassLessons.objects.filter(id__in = request.user.get_profile().following_eclass_lessons.all()).order_by('faculty', '-ltype', 'name')
    return render_to_response('eclass.html', {
            'eclass_lessons': eclass_lessons,
        }, context_instance = RequestContext(request))
