# -*- coding: utf-8 -*-

from cronos.login.forms import *
from cronos.libraries.log import CronosError
from django import http
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

def mylogin(request):
    msg = None
    form = None
    user = None
    if request.method == "POST":
        if request.POST.get('signup'):
            return HttpResponseRedirect('/signup')
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = authenticate(username = username, password = password)
            if user.is_active:
                login(request, user)
                if not request.POST.get('remember'):
                    request.session.set_expiry(0)
                return HttpResponseRedirect('/user')
        except CronosError as error:
            msg = error.value
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/user')
        else:
            form = LoginForm()
    return render_to_response('login.html', {
            'msg': msg,
            'form': form,
        }, context_instance = RequestContext(request))

def mylogout(request):
    logout(request)
    return HttpResponseRedirect('/')

# override 500 error page, in order to pass MEDIA_URL to Context
def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(RequestContext(request, {'request_path': request.path})))
