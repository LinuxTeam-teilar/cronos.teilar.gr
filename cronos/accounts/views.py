# -*- coding: utf-8 -*-

from cronos import Cronos
from cronos.common.exceptions import CronosError, LoginError
from cronos.common.log import log_extra_data
from cronos.common.encryption import encrypt_password, decrypt_password
from cronos.accounts.forms import *
from cronos.accounts.models import UserProfile
from cronos.teilar.models import Teachers, Websites
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from tastypie.models import ApiKey
import logging

logger = logging.getLogger('cronos')

def accounts_login(request):
    '''
    The login page (also the front page)
    '''
    notification = {}
    form = None
    user = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
        else:
            username = None
            password = None
        try:
            '''
            Perform authentication, if it retrieves a user object then
            it was successful. If it retrieves None then it failed to login
            '''
            user = authenticate(username = username, password = password, request = request)
            if not user:
                raise LoginError
            if user.is_active:
                login(request, user)
                if not form.cleaned_data['remember']:
                    request.session.set_expiry(0)
                return HttpResponseRedirect('/')
        except (CronosError, LoginError) as error:
            notification['error'] = error.value
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        else:
            form = LoginForm()
    return render_to_response('login.html', {
       'notification': notification,
       'form': form,
        }, context_instance = RequestContext(request))

@login_required
def accounts_index(request):
    '''
    The frontpage for logged in users. Displays some personal info only.
    '''
    return render_to_response('index.html', {
        'dep_id': request.user.get_profile().school.url.split('=')[1]
        }, context_instance = RequestContext(request))


@login_required
def settings_accounts(request):
    '''
    The user's accounts settings webpage
    '''
    notification = {}
    eclass_credentials_form = EclassCredentialsForm()
    webmail_form = WebmailForm()
    declaration_form = DeclarationForm()
    grades_form = GradesForm()
    eclass_lessons_form = EclassLessonsForm()
    if request.user.get_profile().dionysos_password:
        raw_dionysos_password = decrypt_password(request.user.get_profile().dionysos_password),
    else:
        raw_dionysos_password = None
    student = Cronos(
        request.user.get_profile().dionysos_username,
        raw_dionysos_password,
    )
    if request.user.get_profile().eclass_username:
        student.eclass_username = request.user.get_profile().eclass_username
        student.eclass_password = decrypt_password(request.user.get_profile().eclass_password)
    if request.method == 'POST':
        if request.POST.get('eclass_password'):
            '''
            Update eclass credentials
            '''
            try:
                eclass_credentials_form = EclassCredentialsForm(request.POST)
                student.eclass_password = request.POST.get('eclass_password')
                if not request.user.get_profile().eclass_username:
                    if eclass_credentials_form.is_valid():
                        student.eclass_username = request.POST.get('eclass_username')
                    else:
                        raise LoginError
                try:
                    '''
                    Check if the e-class.teilar.gr credentials already exist in the DB,
                    but belong to another student's account
                    '''
                    user = User.objects.get(userprofile__eclass_username = student.eclass_username)
                    if user.username != request.user.username:
                        raise CronosError(u'Τα στοιχεία e-class.teilar.gr ανήκουν ήδη σε κάποιον άλλο λογαριασμό')
                except User.DoesNotExist:
                    pass
                request.user.get_profile().eclass_username = student.eclass_username
                request.user.get_profile().eclass_password = encrypt_password(student.eclass_password)
                request.user.get_profile().save()
                student.get_eclass_lessons(request)
                notification['success'] = u'Η ανανέωση των στοιχείων openclass.teilar.gr ήταν επιτυχής'
            except (CronosError, LoginError) as error:
                notification['error'] = error.value
        elif request.POST.get('webmail_password'):
            '''
            Update webmail credentials
            '''
            try:
                webmail_form = WebmailForm(request.POST)
                webmail_password = request.POST.get('webmail_password')
                if request.user.get_profile().webmail_username:
                    webmail_username = request.user.get_profile().webmail_username
                else:
                    if not webmail_form.is_valid():
                        raise LoginError
                    webmail_username = request.POST.get('webmail_username')
                try:
                    '''
                    Check if the myweb.teilar.gr credentials already exist in the DB,
                    but belong to another student's account
                    '''
                    user = User.objects.get(userprofile__webmail_username = webmail_username)
                    if user.username != request.user.username:
                        raise CronosError(u'Τα στοιχεία webmail.teilar.gr ανήκουν ήδη σε κάποιον άλλο λογαριασμό')
                except User.DoesNotExist:
                    user = None
                if not user:
                    user = UserProfile.objects.get(pk=request.user.id)
                user.webmail_username = webmail_username
                user.webmail_password = encrypt_password(webmail_password)
                '''
                Login was successful, add in DB
                '''
                user.save()
                notification['success'] = u'Η ανανέωση των στοιχείων myweb.teilar.gr ήταν επιτυχής'
            except (CronosError, LoginError) as error:
                notification['error'] = error.value
        elif request.POST.get('declaration'):
            '''
            Update the declaration
            '''
            try:
                student.get_dionysos_declaration(request)
                request.user.get_profile().declaration = student.dionysos_declaration
                request.user.get_profile().save()
                notification['success'] = u'Η ανανέωση της δήλωσης ήταν επιτυχής'
            except (CronosError, LoginError) as error:
                notification['error'] = error.value
        elif request.POST.get('grades'):
            '''
            Update the grades
            '''
            try:
                student.get_dionysos_grades(request)
                request.user.get_profile().grades = student.dionysos_grades
                request.user.get_profile().save()
                notification['success'] = u'Η ανανέωση της βαθμολογίας ήταν επιτυχής'
            except (CronosError, LoginError) as error:
                notification['error'] = error.value
        elif request.POST.get('eclass_lessons'):
            '''
            Update the eclass lessons
            '''
            try:
                student.get_eclass_lessons(request)
                notification['success'] = u'Η ανανέωση των μαθημάτων e-class ήταν επιτυχής'
            except (CronosError, LoginError) as error:
                notification['error'] = error.value
    return render_to_response('settings_accounts.html',{
        'notification': notification,
        'eclass_credentials_form': eclass_credentials_form,
        'webmail_form': webmail_form,
        'eclass_lessons_form': eclass_lessons_form,
        'declaration_form': declaration_form,
        'grades_form': grades_form,
       }, context_instance = RequestContext(request))

@login_required
def settings_announcements(request):
    '''
    The user's announcements settings webpage
    '''
    notification = {}
    '''
    Fill the select boxes with teachers
    '''
    teachers_all_q = Teachers.objects.filter(is_active = True).order_by('name')
    '''
    Get the following teachers that will be put in the right selectbox
    '''
    teachers_following = teachers_all_q.filter(id__in = request.user.get_profile().following_teachers.all())
    '''
    Get the not following teachers that will be put in the left selectbox
    '''
    teachers_unfollowing = teachers_all_q.exclude(id__in = request.user.get_profile().following_teachers.all())
    '''
    Fill the select boxes with websites
    '''
    websites_all_q = Websites.objects.filter(is_active = True).exclude(url__endswith = u'_dummy').order_by('name')
    '''
    Get the following websites that will be put in the right selectbox
    '''
    websites_following = websites_all_q.filter(id__in = request.user.get_profile().following_websites.all())
    '''
    Get the not following websites that will be put in the left selectbox
    '''
    websites_unfollowing = websites_all_q.exclude(id__in = request.user.get_profile().following_websites.all())
    '''
    Process one of the form submissions
    '''
    if request.method == 'POST':
        if request.POST.get('teachers_selected'):
            '''
            Get the list of selected teachers
            '''
            selected_teachers = dict(request.POST)['teachers_selected']
            selected_teachers = teachers_all_q.filter(id__in = selected_teachers)
            '''
            Find the teachers for addition to the following_teachers field
            '''
            teachers_for_addition = selected_teachers.exclude(id__in = teachers_following)
            for teacher in teachers_for_addition:
                request.user.get_profile().following_teachers.add(teacher)
            teachers_for_removal = teachers_following.exclude(id__in = selected_teachers)
            '''
            Find the teachers for removal from the following_teachers field
            '''
            for teacher in teachers_for_removal:
                request.user.get_profile().following_teachers.remove(teacher)
        else:
            request.user.get_profile().following_teachers.clear()
        if request.POST.get('websites_selected'):
            '''
            Get the list of selected websites
            '''
            selected_websites = dict(request.POST)['websites_selected']
            selected_websites = websites_all_q.filter(id__in = selected_websites)
            '''
            Find the websites for addition to the following_websites field
            '''
            websites_for_addition = selected_websites.exclude(id__in = websites_following)
            for website in websites_for_addition:
                request.user.get_profile().following_websites.add(website)
            '''
            Find the websites for removal from the following_websites field
            '''
            websites_for_removal = websites_following.exclude(id__in = selected_websites)
            for website in websites_for_removal:
                request.user.get_profile().following_websites.remove(website)
        else:
            request.user.get_profile().following_websites.clear()
        notification['success'] = u'Οι αλλαγές έγιναν επιτυχώς'
    return render_to_response('settings_announcements.html',{
        'notification': notification,
        'teachers_unfollowing': teachers_unfollowing,
        'teachers_following': teachers_following,
        'websites_unfollowing': websites_unfollowing,
        'websites_following': websites_following,
        }, context_instance = RequestContext(request))

@login_required
def settings_apikey(request):
    notification = {}
    '''
    Get the API key
    '''
    try:
        api_key = ApiKey.objects.get(user = request.user)
        api_key_hash = api_key.key
    except ApiKey.DoesNotExist:
        api_key = None
        api_key_hash = None
    if request.method == 'POST':
        if request.POST.get('api_key'):
            if api_key:
                api_key.key = api_key.generate_key()
                api_key.save()
            else:
                api_key = ApiKey.objects.create(user=request.user)
            api_key_hash = api_key.key
        notification['success'] = u'Το API key ανανεώθηκε επιτυχώς'
    return render_to_response('settings_apikey.html',{
        'notification': notification,
        'api_key': api_key_hash,
        }, context_instance = RequestContext(request))
