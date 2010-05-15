# -*- coding: utf-8 -*-

import pycurl
import StringIO
import urllib
import os
import urlparse
from cronos.passwords import *
from cronos.webmail.forms import *
from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

b = StringIO.StringIO()
conn = pycurl.Curl()
cookie_file_name = os.tempnam('/tmp','webmail')
login_form_data = urllib.urlencode(login('webmail'))
conn.setopt(pycurl.FOLLOWLOCATION, 0)
conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
conn.setopt(pycurl.URL, 'http://myweb.teilar.gr')
conn.setopt(pycurl.POST, 0)
conn.perform()
conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/redirect.php')
conn.setopt(pycurl.POST, 1)
conn.setopt(pycurl.POSTFIELDS, login_form_data)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
conn.perform()
output = (b.getvalue()).decode('iso-8859-7')
#print output

soup = BeautifulSoup(output).findAll('table')[9]
soup1 = soup.findAll('a')
title = ''
for item in xrange(3, len(soup1)):
	title += '<br />'
	title += '<a href="?passed_id='+str(soup1[item]).split('"')[1].split('&amp;')[1].split('=')[1]+'">test</a>'
def webmail(request):
	template = get_template('webmail_readbody.html')
	variables = Context({
		'content': title,
	})
	output = template.render(variables)
	return HttpResponse(output)

def passed_id(request):
	if request.method == 'GET':
		form = MailForm(request.GET)
		if form.is_valid():
			link = 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=' + str(request.GET.get('passed_id')) + '&startMessage=1'
			b = StringIO.StringIO()
			cookie_file_name = os.tempnam('/tmp','webmail')
			login_form_data = urllib.urlencode(login('webmail'))
			conn.setopt(pycurl.FOLLOWLOCATION, 0)
			conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
			conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
			conn.setopt(pycurl.URL, 'http://myweb.teilar.gr')
			conn.setopt(pycurl.POST, 0)
			conn.perform()
			conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/redirect.php')
			conn.setopt(pycurl.POST, 1)
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			conn.setopt(pycurl.URL, link)
			conn.perform()
			output = (b.getvalue()).decode('iso-8859-7')
			'''
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')
			print output'''
			'''b = StringIO.StringIO()
			conn.setopt(pycurl.FOLLOWLOCATION, 1)
			conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
			conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
			conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=178&startMessage=1')
			conn.setopt(pycurl.POST, 1)
			conn.setopt(pycurl.COOKIE, cookie_file_name)
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')'''
			template = get_template('test.html')
			variables = Context({
				'content': output,
			})
			output = template.render(variables)
#			print output
			return HttpResponse(output)
	else:
		form = MailForm()
	return render_to_response('webmail_readbody.html', {'form': form, } )
