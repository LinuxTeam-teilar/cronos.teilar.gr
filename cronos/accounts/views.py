# -*- coding: utf-8 -*-

from cronos import CronosError, log_extra_data
from cronos.accounts.forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
import logging

logger = logging.getLogger('cronos')

def about(request):
    '''
    The About webpage
    '''
    return render_to_response('about.html', {},
        context_instance = RequestContext(request))

def server_error(request, template_name='500.html'):
    '''
    500 error handler.
    Override 500 error page, in order to pass MEDIA_URL to Context
    '''
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request, {'request_path': request.path})))

@login_required
def accounts_index(request):
    '''
    The frontpage for logged in users. Displays some personal info only.
    '''
    return render_to_response('index.html', {
        }, context_instance = RequestContext(request))


@login_required
def accounts_settings(request):
    '''
    The user settings webpage
    '''
    '''
    Initialize variables and forms, in order to show them empty every time the
    webpage is loaded
    '''
    msg = None
    eclass_credentials_form = EclassCredentialsForm()
    webmail_form = WebmailForm()
    declaration_form = DeclarationForm()
    grades_form = GradesForm()
    eclass_lessons_form = EclassLessonsForm()
    if request.method == 'POST':
        try:
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
                        user = UserProfile.objects.get(user__eclass_username = request.POST.get('eclass_username'))
                        if user.username != request.user.username:
                            raise CronosError('Τα στοιχεία e-class.teilar.gr υπάρχουν ήδη σε κάποιον άλλο λογαριασμό')
                    except User.DoesNotExist:
                        pass
                    '''
                    Check if the credentials are correct
                    '''
                    output = eclass_login(request.POST.get('eclass_username'), request.POST.get('eclass_password'))
                    if output:
                        '''
                        Credentials are correct, update them along with the
                        eclass lessons list
                        '''
                        eclass_lessons = get_eclass_lessons(output)
                        user = UserProfile.objects.get(user__username = request.user.username)
                        user.eclass_username = request.POST.get('eclass_username')
                        user.eclass_password = encrypt_password(request.POST.get('eclass_password'))
                        user.eclass_lessons = ','.join(eclass_lessons)
                        user.save()
                        msg = 'Η ανανέωση των στοιχείων e-class.teilar.gr ήταν επιτυχής'
                    else:
                        raise CronosError('Τα στοιχεία δεν επαληθεύτηκαν από το e-class.teilar.gr')
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
                    output = webmail_login(0, request.POST.get('webmail_username'), request.POST.get('webmail_password'))
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
#            elif str(request.POST) == str('<QueryDict: {u\'declaration\': [u\'\']}>'):
#                declaration_form = DeclarationForm(request.POST)

        except Exception as Error:
            logger.error(error, extra = log_extra_data())
            raise CronosError('Παρουσιάστηκε σφάλμα')
    return render_to_response('preferences.html',{
        'msg': msg,
        'eclass_credentials_form': eclass_credentials_form,
        'eclass_lessons_form': eclass_lessons_form,
        'webmail_form': webmail_form,
        }, context_instance = RequestContext(request))
