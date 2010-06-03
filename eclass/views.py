# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import urllib
import os
import urlparse
from cronos.passwords import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def eclass(request):
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	login_form_data = urllib.urlencode(login('eclass'))
	conn.setopt(pycurl.FOLLOWLOCATION, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.URL, 'http://e-class.teilar.gr/index.php')
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)
	header = []
	for i in xrange(len(soup.findAll('th', 'persoBoxTitle'))):
		header.append(soup.findAll('th', 'persoBoxTitle')[i].contents[0])
	return render_to_response('eclass.html', {
			'head_title': 'Eclass | ',
			'header': header,
		}, context_instance = RequestContext(request))
