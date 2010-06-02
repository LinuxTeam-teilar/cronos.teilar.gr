# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import urllib
import os
import urlparse
from cronos.passwords import *
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


b = StringIO.StringIO()
conn = pycurl.Curl()
cookie_file_name = os.tempnam('/tmp','dionysos')
login_form_data = urllib.urlencode(login('dionysos'))
conn.setopt(pycurl.FOLLOWLOCATION, 1)
conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/')
conn.setopt(pycurl.POST, 0)
conn.perform()
conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/login.asp')
conn.setopt(pycurl.POST, 1)
conn.setopt(pycurl.POSTFIELDS, login_form_data)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = (b.getvalue()).decode('windows-1253')
soup = BeautifulSoup(output)


soup1 = BeautifulSoup(str(soup.findAll('table')[13]))
username = str(soup1.findAll('td')[1].contents[0])
soup2 = BeautifulSoup(str(soup1.findAll('tr')[5]))
lname = str(soup2.findAll('td')[1].contents[0])
soup2 = BeautifulSoup(str(soup1.findAll('tr')[6]))
fname = str(soup2.findAll('td')[1].contents[0])
soup2 = BeautifulSoup(str(soup1.findAll('tr')[7]))
am = str(soup2.findAll('td')[1].contents[0])
soup2 = BeautifulSoup(str(soup1.findAll('tr')[9]))
eksamino = str(soup2.findAll('td')[1].contents[0])
soup2 = BeautifulSoup(str(soup.findAll('table')[15]))
intr_year = str(eisagogi1.findAll('span','tablecell')[0].contents[0].split('-')[0]) + str(souptest.findAll('span','tablecell')[1].contents[0])[:2]



b = StringIO.StringIO()
conn.setopt(pycurl.URL, 'http://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&')
conn.setopt(pycurl.POST, 1)
conn.setopt(pycurl.POSTFILEDS, login_form_data)
conn.setopt(pycurl.COOKIE, cookie_file_name)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = (b.getvalue()).decode('windows-1253')

soup = BeautifulSoup(output)
soup1 = BeautifulSoup(str(soup.findAll('table')[13]))
i = 0
dilosi = ''
for item in soup1.findAll('span', 'underline'):
	dilosi += str(soup1.findAll('span', 'underline')[i].contents[0])
	dilosi += '<br />'
	i += 1

def dionysos(request):
	template = get_template('dionysos.html')
	variables = Context({
		'head_title': 'poseidon.teilar.gr',
		'username': username,
		'lname': lname,
		'fname': fname,
		'am': am,
		'eksamino': eksamino,
		'dilosi': dilosi,
	})
	output = template.render(variables)
	return HttpResponse(output)

def top(request):
	template = get_template('top.html')
	variables = Context({
		'head_title': 'poseidon.teilar.gr',
		'username': username,
		'lname': lname,
		'fname': fname,
	})
	output = template.render(variables)
	return HttpResponse(output)
