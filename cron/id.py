# -*- coding: utf-8 -*-
from proj_root import *
import sys
import os
sys.path.append(PROJ_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import urllib
import urlparse
import re
import MySQLdb
from cronos.passwords import *
from cronos.announcements.models import *

conn = pycurl.Curl()
p = re.compile(r'<[^<]*?/?>')

### www.teilar.gr ###

for cid in xrange(30):
	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, 'http://www.teilar.gr/tmimatanews.php?cid=' + str(cid))
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)
	try:
		school = str(soup.findAll('td', 'BlueTextBold')[0])
		school = p.sub(' ', school)
	except:
		pass
	if (cid == 0):
		school = 'Κεντρική Σελίδα ΤΕΙ Λάρισας'
	if (len(school) > 5):
		depart = Id(
			urlid = 'cid' + str(cid),
			name = school.strip(),
			department = '',
			email = '',
		)
	try:
		depart.save()
	except MySQLdb.IntegrityError:
		pass

# extra sites #
dest = [
	['noc', 'Κέντρο Διαχείρισης Δικτύου'],
	['career', 'Γραφείο Διασύνδεσης'],
	['linuxteam', 'Linux Team'],
	['dionysos', 'Πρόγραμμα Γραμματείας']
	['library', 'Κεντρική Βιβλιοθήκη']
	['pr', 'Γραφείο Δημοσίων και Διεθνών Σχέσεων']
	]

for i in xrange(len(dest[:][:])):
	dest[i][0] = Id(
		urlid = 'cid' + str(50+i),
		name = str(dest[i][1]) +  ' ΤΕΙ Λάρισας',
		department = '',
		email = '',
	)

	try:
		dest[i][0].save()
	except MySQLdb.IntegrityError:
		pass	

### www.teilar.gr/profannews.php ###

for pid in xrange(350):
	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, 'http://www.teilar.gr/person.php?pid=' + str(pid))
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)
	teacher = ''
	email = ''
	depart = ''
	try:
		teacher = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11Bold')[1].contents[0])))
		email = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11')[5])).a.contents[0])
		depart = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11')[2])))
		depart = p.sub('',depart)
	except:
		pass
	if (len(teacher) > 1):
		teachers = Id(
			urlid = 'pid' + str(pid),
			name = teacher,
			department = depart,
			email = email,
		)
		try:
			teachers.save()
		except MySQLdb.IntegrityError:
			pass

### e-class.teilar.gr ###

b = StringIO.StringIO()
cookie_file_name = os.tempnam('/tmp', 'eclass')
login_form_data = urllib.urlencode(login('eclass'))
conn.setopt(pycurl.FOLLOWLOCATION, 1)
conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
conn.setopt(pycurl.URL, 'http://openclass.teilar.gr/index.php')
conn.setopt(pycurl.POST, 1)
conn.setopt(pycurl.POSTFIELDS, login_form_data)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = unicode(b.getvalue(), 'utf-8', 'ignore')
soup = BeautifulSoup(output).find('table', 'FormData')

i = 0

for item in soup.findAll('a'):
	if (i%2 == 0):
		cid = str(soup.findAll('a')[i].contents[0]).split('-')[0]

		lesson = ''
		for j in xrange(len((soup.findAll('a')[i].contents[0]).split('-')) - 1):
			lesson += str(soup.findAll('a')[i].contents[0]).split('-')[j+1].strip() + ' '

		eclass = Id(
			urlid = str(cid),
			name = 'e-class: ' + lesson.strip(),
			department = '',
			email = '',
		)

		try:
			eclass.save()
		except MySQLdb.IntegrityError:
			pass
	
	i += 1
