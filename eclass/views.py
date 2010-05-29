# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import urllib
import os
import urlparse
from cronos.passwords import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

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
a = []
for i in xrange(len(soup.findAll('th', 'persoBoxTitle'))):
	a.append(soup.findAll('th', 'persoBoxTitle')[i].contents[0])

@login_required
def eclass(request):
	template = get_template('eclass.html')
	variables = Context({
		'a': a,
	})
	output = template.render(variables)
	return HttpResponse(output)
