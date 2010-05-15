# -*- coding: utf-8 -*-

import pycurl
import httplib
import urllib
import StringIO
from cronos.library.forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

def search(request):
#	link = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=10&ipp=20&spp=20&profile=multbl--1&ri=&term=' + str(request.POST.get('page',1)) + '&index=.GEN&x=0&y=0&aspect=subtab22'
	link = 'http://linuxteam.cs.teilar.gr/search/node/'
	print link
	if request.method == 'GET':
		form = SearchForm(request.GET)
		if form.is_valid():
			'''b = StringIO.StringIO()
			conn = pycurl.Curl()
			conn.setopt(pycurl.FOLLOWLOCATION, 1)
			conn.setopt(pycurl.URL, link)
			conn.setopt(pycurl.POST, 1)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')'''
			return HttpResponseRedirect(link + request.GET.get('search'))
	else:
		form = SearchForm()
	return render_to_response('library.html', {'form': form, } )
