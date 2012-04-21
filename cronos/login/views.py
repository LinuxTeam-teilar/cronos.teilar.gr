# -*- coding: utf-8 -*-

from cronos.login.forms import LoginForm
from cronos.log import CronosError
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

def cronos_login(request):
    msg = None
    form = None
    user = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            user = authenticate(username = username, password = password, request = request, form = form)
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

def server_error(request, template_name='500.html'):
    '''
    500 error handler.
    Override 500 error page, in order to pass MEDIA_URL to Context
    '''
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request, {'request_path': request.path})))
