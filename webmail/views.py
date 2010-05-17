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
#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX')
conn.perform()
output = (b.getvalue()).decode('iso-8859-7')

soup = BeautifulSoup(output).findAll('table')[9]
soup1 = soup.findAll('tr')
mail = []
mail1 = ''

for i in xrange(len(soup1)-1):
	if (len(str(soup1[i+1].find('a'))) > 4):
			mail.append([])
#		for j in xrange(5):
			# sender
			sender = str(soup1[i+1].findAll('td')[1].contents[0].contents[0])
			mail[i].append(sender)
			# passed_id
			passed_id = str(soup1[i+1].find('a')).split('&amp;')[1].replace('passed_id=', '')
			mail[i].append(passed_id)
			# time
			time = str(soup1[i+1].findAll('td')[2].contents[0])
			mail[i].append(time)
			# title
			title = str(soup1[i+1].findAll('td')[4].a.contents[0])
			mail[i].append(title)
			# full title
#			if (soup1[i].findall('td')[4].split('"')[2] is None):
#				full_title = soup1[i].findAll('td')[4].split('"')[3]
#				mail[i-1].append(full_title)
#			else:
			full_title = ''
			mail[i].append('')
			print mail[i]
			mail1 += '<br />' + sender + '<br />' + time + '<br /><a href="/mail?passed_id=' + passed_id + 'title ="' + full_title + '">' + title + '</a>'

def webmail(request):
	template = get_template('webmail_readbody.html')
	variables = Context({
		'content': mail1,
	})
	output = template.render(variables)
	return HttpResponse(output)

'''def passed_id(request):
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
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')
			print output
			b = StringIO.StringIO()
			conn.setopt(pycurl.FOLLOWLOCATION, 1)
			conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
			conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
			conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=178&startMessage=1')
			conn.setopt(pycurl.POST, 1)
			conn.setopt(pycurl.COOKIE, cookie_file_name)
			conn.setopt(pycurl.POSTFIELDS, login_form_data)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')
			template = get_template('test.html')
			variables = Context({
				'content': output,
			})
			output = template.render(variables)
#			print output
			return HttpResponse(output)
	else:
		form = MailForm()
	return render_to_response('webmail_readbody.html', {'form': form, } )'''
