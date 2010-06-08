# -*- coding: utf-8 -*-

import pycurl
import StringIO
import urllib
import os
import urlparse
import base64
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from cronos.webmail.forms import *
from BeautifulSoup import BeautifulSoup
from django.shortcuts import render_to_response
from django.template import RequestContext

def webmail_login(request, link):
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	cookie_file_name = os.tempnam('/tmp','webmail')
	login_form_seq = [
		('login_username', request.user.get_profile().webmail_username),
		('secretkey', base64.b64decode(request.user.get_profile().webmail_password)),
		('js_autodetect_results', '1'),
		('just_logged_in', '1')
	]
	login_form_data = urllib.urlencode(login_form_seq)
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
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX')
	conn.perform()
	output = (b.getvalue()).decode('iso-8859-7')
	return output

@login_required
def webmail(request):
	id = ''
	if (request.GET.get('passed_id')):
		form = MailForm(request.GET)
		link = 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=' + str(request.GET.get('passed_id')) + '&startMessage=1'
		output = webmail_login(request, link)
		mail = BeautifulSoup(output).findAll('table')[7]
		id = request.GET.get('passed_id')
	else:
		form = MailForm()
		link = 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX'
		output = webmail_login(request, link)
		soup = BeautifulSoup(output).findAll('table')[9]
		soup1 = soup.findAll('tr')
		mail = []
		k = 0
		for i in xrange(1, len(soup1)):
			if (len(str(soup1[i].find('a'))) > 4):
				sender_name = str(soup1[i].findAll('td')[1].contents[0].contents[0])
				sender_mail = str(soup1[i].findAll('td')[1]).split('"')[5]
				passed_id = str(soup1[i].find('a')).split('&amp;')[1].replace('passed_id=', '')
				time = str(soup1[i].findAll('td')[2].contents[0])
				title = str(soup1[i].findAll('td')[4].a.contents[0])
				try:
					full_title = str(soup1[i].findAll('td')[4].a).split('"')[3]
				except (TypeError, IndexError):
					full_title = ''
				mail.append([sender_mail, sender_name, time, passed_id, full_title, title])
	return render_to_response('webmail.html', {
			'form': form,
			'items': mail,
			'id': id
		}, context_instance = RequestContext(request))
