# -*- coding: utf-8 -*-

import pycurl
import StringIO
import urllib
import os
import urlparse
from types import *
from cronos.passwords import *
from cronos.webmail.forms import *
from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

def webmail_login(link):
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
	conn.setopt(pycurl.URL, link)
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX')
	conn.perform()
	output = (b.getvalue()).decode('iso-8859-7')
	return output

def webmail(request):
	form = MailForm(request.GET)
	if (len(str(request.GET.get('passed_id'))) == 3):
		link = 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=' + str(request.GET.get('passed_id')) + '&startMessage=1'
		output = webmail_login(link)

		soup = BeautifulSoup(output).findAll('table')[7]
		template = get_template('webmail.html')
		variables = Context({
			'passed_id': 'set',
			'content': soup,
		})
		output = template.render(variables)
		return HttpResponse(output)
	else:
		link = 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX'
		output = webmail_login(link)

		soup = BeautifulSoup(output).findAll('table')[9]
		soup1 = soup.findAll('tr')
		mail = []
		mail1 = []
		k = 0

		for i in xrange(1, len(soup1)):
			if (len(str(soup1[i].find('a'))) > 4):
				mail.append([])
				sender_name = str(soup1[i].findAll('td')[1].contents[0].contents[0])
				sender_mail = str(soup1[i].findAll('td')[1]).split('"')[5]
				passed_id = str(soup1[i].find('a')).split('&amp;')[1].replace('passed_id=', '')
				time = str(soup1[i].findAll('td')[2].contents[0])
				title = str(soup1[i].findAll('td')[4].a.contents[0])
				try:
					full_title = str(soup1[i].findAll('td')[4].a).split('"')[3]
				except (TypeError, IndexError):
					full_title = ''
				mail1 = [sender_mail, sender_name, time, passed_id, full_title, title]
				for j in xrange(6):
					mail[k].append(mail1[j][:])
				k+=1

		template = get_template('webmail.html')
		variables = Context({
			'mail': mail,
		})
		output = template.render(variables)
		return HttpResponse(output)
	return render_to_response('webmail.html', {'form': form, } )
