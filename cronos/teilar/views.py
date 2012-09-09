# -*- coding: utf-8 -*-

from cronos.teilar.forms import LibraryForm
from cronos.teilar.models import Teachers
from cronos import teilar_anon_login
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
        teacher.url = teacher.url.split('=')[1]
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
            output = teilar_anon_login(url)
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
    declaration_lessons = []
    if request.user.get_profile().declaration:
        declaration_full = request.user.get_profile().declaration.split(':')
        i = 0
        while i <= len(declaration_full):
            declaration_lessons.append(declaration_full[i:i+7])
            i += 7

    '''
    Retrieve and print the grades
    '''
    grades = []
    summary = None
    total = None
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
    return  render_to_response('dionysos.html', {
            'summary': summary,
            'declaration_lessons': declaration_lessons,
            'grades': grades,
            'total': total,
        }, context_instance = RequestContext(request))

@login_required
def eclass(request):
    try:
        output = eclass_login(request.user.get_profile().eclass_username, decryptPassword(request.user.get_profile().eclass_password))
        soup = BeautifulSoup(output)

        soup1 = BeautifulSoup(str(soup.findAll('tr', 'odd')[3]))
        deadlines = []
        i = 0
        for item in soup1.findAll('li', 'category'):
            lesson = item.contents[0]
            title = soup1.findAll('a', 'square_bullet2')[i].contents[0].contents[0]
            date = soup1.findAll('p', 'content_pos')[i].b.contents[0]
            status = soup1.findAll('span')[i].contents[0]
            deadlines.append([lesson, title, date, status])
            i += 1
    except:
        deadlines = None

    try:
        soup1 = BeautifulSoup(str(soup.findAll('tr', 'odd')[4]))
        documents = []
        i = 0
        j = 0
        for item in soup1.findAll('li'):
            if item in soup1.findAll('li', 'category'):
                lesson = item.contents[0]
                i += 1
            else:
                title = soup1.findAll('a', 'square_bullet2')[j].contents[0].contents[0].split(' - (')[0]
                date = soup1.findAll('a', 'square_bullet2')[j].contents[0].contents[0].split(' - (')[1][:-1]
                documents.append([lesson, title, date])
                j += 1
    except:
        documents = None

    eclass_lessons = []
    for item in Id.objects.filter(urlid__in = request.user.get_profile().eclass_lessons.split(',')):
        eclass_lessons.append([item.urlid.strip(), item.name])

    return render_to_response('eclass.html', {
            'headers': ['ΤΑ ΜΑΘΗΜΑΤΑ ΜΟΥ', 'ΟΙ ΔΙΟΡΙΕΣ ΜΟΥ', 'ΤΑ ΤΕΛΕΥΤΑΙΑ ΜΟΥ ΕΓΓΡΑΦΑ'],
            'eclass_lessons': eclass_lessons,
            'deadlines': deadlines,
            'documents': documents,
        }, context_instance = RequestContext(request))
