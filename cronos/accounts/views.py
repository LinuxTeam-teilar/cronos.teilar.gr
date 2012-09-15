# -*- coding: utf-8 -*-

from cronos import eclass_auth_login
from cronos.common.log import CronosError, log_extra_data
from cronos.common.encryption import encrypt_password
from cronos.accounts.forms import *
from cronos.accounts.models import UserProfile
from cronos.teilar.models import Teachers, Websites
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging

logger = logging.getLogger('cronos')

def accounts_login(request):
    '''
    The login page (also the front page)
    '''
    msg = None
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
                raise CronosError(u'Λάθος στοιχεία')
            if user.is_active:
                login(request, user)
                if not form.cleaned_data['remember']:
                    request.session.set_expiry(0)
                return HttpResponseRedirect('/')
        except CronosError as error:
            msg = error.value
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/')
        else:
            form = LoginForm()
    return render_to_response('login.html', {
       'msg': msg,
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
def settings(request):
    '''
    The user's settings webpage
    '''
    msg = None
    eclass_credentials_form = EclassCredentialsForm()
    webmail_form = WebmailForm()
    declaration_form = DeclarationForm()
    grades_form = GradesForm()
    eclass_lessons_form = EclassLessonsForm()
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
        if request.POST.get('eclass_username'):
            '''
            Update eclass credentials
            '''
            eclass_credentials_form = EclassCredentialsForm(request.POST)
            if eclass_credentials_form.is_valid():
                '''
                Check if the e-class.teilar.gr credentials already exist in the DB,
                but belong to another student's account
                '''
                try:
                    user = User.objects.get(userprofile__eclass_username = request.POST.get('eclass_username'))
                    if user.username != request.user.username:
                        raise CronosError(u'Τα στοιχεία e-class.teilar.gr ανήκουν ήδη σε κάποιον άλλο λογαριασμό')
                except User.DoesNotExist:
                    pass
                '''
                Check if the credentials are correct
                '''
                try:
                    output = eclass_auth_login(request.POST.get('eclass_username'), request.POST.get('eclass_password'))
                    if output:
                        '''
                        Credentials are correct, update them along with the
                        eclass lessons list
                        '''
    #                    eclass_lessons = get_eclass_lessons(output)
                        user = UserProfile.objects.get(pk=request.user.id)
                        user.eclass_username = request.POST.get('eclass_username')
                        user.eclass_password = encrypt_password(request.POST.get('eclass_password'))
                        user.save()
    #                    user.eclass_lessons = ','.join(eclass_lessons)
                        msg = u'Η ανανέωση των στοιχείων openclass.teilar.gr ήταν επιτυχής'
                    else:
                        msg = u'Λάθος στοιχεία openclass'
                except CronosError as error:
                    msg = error.value
        elif request.POST.get('webmail_username'):
            '''
            Check if the myweb.teilar.gr credentials already exist in the DB,
            but belong to another student's account
            '''
            try:
                user = UserProfile.objects.get(user__webmail_username = request.POST.get('webmail_username'))
                if user.username != request.user.username:
                    raise CronosError('Τα στοιχεία myweb.teilar.gr υπάρχουν ήδη σε κάποιον άλλο λογαριασμό')
            except User.DoesNotExist:
                pass
            '''
            Update myweb.teilar.gr credentials
            '''
            webmail_form = WebmailForm(request.POST)
            if webmail_form.is_valid():
                '''
                Check if the credentials are correct
                '''
                output = webmail_auth_login(0, request.POST.get('webmail_username'), request.POST.get('webmail_password'))
                if output:
                    '''
                    Credentials are correct, update them
                    '''
                    user = UserProfile.objects.get(user__username == request.user.username)
                    user.webmail_username = request.POST.get('webmail_username')
                    user.webmail_password = request.POST.get('webmail_password')
                    user.save()
                    msg = 'Η ανανέωση των στοιχείων myweb.teilar.gr ήταν επιτυχής'
                else:
                    raise CronosError('Τα στοιχεία δεν επαληθεύτηκαν από το myweb.teilar.gr')
        elif request.POST.get('teachers'):
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
            msg = u'Οι αλλαγές έγιναν επιτυχώς'
        elif request.POST.get('websites'):
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
            msg = u'Οι αλλαγές έγιναν επιτυχώς'
    return render_to_response('settings.html',{
        'msg': msg,
        'eclass_credentials_form': eclass_credentials_form,
        'eclass_lessons_form': eclass_lessons_form,
        'webmail_form': webmail_form,
        'teachers_unfollowing': teachers_unfollowing,
        'teachers_following': teachers_following,
        'websites_unfollowing': websites_unfollowing,
        'websites_following': websites_following,
        }, context_instance = RequestContext(request))
