# -*- coding: utf-8 -*-

from cronos.refrigerators.forms import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from cronos.refrigerators.__init__ import *

def refrigerators(request):
    varDict = procReq(request)
    # 'XMLFILENAME' will be replaced by the urls./extensions(ex-refrigerators)
    # /UserSelectedURL(e.g. refiregerators)/.
    return render_to_response(""'XMLFILENAME'"", varDict}, context_instance = RequestContext(request))
