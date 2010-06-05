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
from cronos.announcements.models import *

conn = pycurl.Curl()
p = re.compile(r'<[^<]*?/?>')

def getid(id, i):
	db = Id.objects.filter(urlid__exact = (id + str(i)))
	for item in db:
		return item

def geteclassid(i):
	db = Id.objects.filter(urlid__exact = i)
	for item in db:
		return item

### www.teilar.gr ###

dest = ['http://www.teilar.gr/']

for cid in xrange(30):
	if (cid != 0):
		dest.append('http://www.teilar.gr/tmimatanews.php?cid=' + str(cid))
	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, dest[cid])
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(str(BeautifulSoup(output).findAll('td', 'LineDownDots')))

	j = 0

	for item in soup.findAll('td', 'LineDownDots'):
		link = 'http://www.teilar.gr/' + str(soup.findAll('td', 'BlackText11')[j].contents[0]).split('"')[3].replace('&amp;', '&')

		#parse each announcement

		b = StringIO.StringIO()
		conn.setopt(pycurl.URL, link)
		conn.setopt(pycurl.WRITEFUNCTION, b.write)
		conn.perform()
		output = unicode(b.getvalue(), 'utf-8', 'ignore')
		soup1 = BeautifulSoup(output)

		main_text = ''
		attach_text = ''
		attach_url = ''

		if len(str(soup1.find('td', 'BlackText11'))) > 5:
			main_text = str(soup1.find('td', 'BlackText11'))
			main_text = p.sub(' ', main_text)   

		if len(str(soup1.find('a', 'BlackText11Bold'))) > 5:
			attach_text = str(soup1.find('a', 'BlackText11Bold').contents[0])
			attach_url = 'http://www.teilar.gr/' + str(soup1.find('a', 'BlackText11Bold')).split('"')[3]

		teilar_gr = Announcements(
			title = str(soup.findAll('a', 'BlackText11')[j].contents[0]).strip(),
			url = link,
			unique = link,
			urlid = getid('cid', cid),
			description = main_text.strip(),
			attachment_text = attach_text,
			attachment_url = attach_url,
		)

		try:
			teilar_gr.save()
		except MySQLdb.IntegrityError:
			pass

		j += 1

### www.teilar.gr/profannnews.php ###

for pid in xrange(350):
	link = 'http://www.teilar.gr/person_announce.php?pid=' + str(pid)

	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, link)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)

	i = 0

	for item in soup.findAll('td', 'LineDownDots'):
		soup1 = BeautifulSoup(str(soup.findAll('td', 'LineDownDots')[i]))
		
		main_text = ''
		attach_text = ''
		attach_url = ''
		unique = ''

		if len(str(soup1.findAll('td', 'BlackText11')[1])) > 5:
			main_text = str(soup1.findAll('td', 'BlackText11')[1])
			main_text = p.sub(' ', main_text)

		try:
			attach_text = str(soup1.findAll('td', 'BlackText11')[2].contents[0].contents[0].contents[0])
			attach_url = 'http://www.teilar.gr/' + str(soup1.findAll('td', 'BlackText11')[2].contents[0].contents[0]).split('"')[3]
		except:
			pass

		if len(main_text) == 0:
			unique = attach_url
		else:
			unique = main_text.strip()

		i += 1

		teachers_teilar_gr = Announcements(
			title = str(soup1.findAll('td', 'BlackText11')[0].contents[0].contents[0]).strip(),
			urlid = getid('pid', pid),
			description = main_text.strip(),
			unique = unique,
			attachment_text = attach_text,
			attachment_url = attach_url,
			url = link,
		)
		
		try:
			teachers_teilar_gr.save()
		except MySQLdb.IntegrityError:
			pass

### e-class.teilar.gr ###

b = StringIO.StringIO()
cookie_file_name = os.tempnam('/tmp', 'eclass')
login_form_seq = [
	('uname', ECLASS_USER),
	('pass', ECLASS_PASSWORD),
	('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82'),
]
login_form_data = urllib.urlencode(login_form_seq)
conn.setopt(pycurl.FOLLOWLOCATION, 1)
conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
conn.setopt(pycurl.URL, 'http://openclass.teilar.gr/index.php')
conn.setopt(pycurl.POST,1)
conn.setopt(pycurl.POSTFIELDS, login_form_data)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = unicode(b.getvalue(), 'utf-8', 'ignore')
soup = BeautifulSoup(output).find('table', 'FormData')

i = 0

for item in soup.findAll('a'):
	if (i%2 == 0):
		cid = str(soup.findAll('a')[i].contents[0]).split('-')[0].strip()
		link = 'http://openclass.teilar.gr/index.php?perso=2&c=' + cid

		b = StringIO.StringIO()
		conn.setopt(pycurl.FOLLOWLOCATION, 1)
		conn.setopt(pycurl.COOKIEFILE, cookie_file_name)
		conn.setopt(pycurl.COOKIEJAR, cookie_file_name)
		conn.setopt(pycurl.URL, link)
		conn.setopt(pycurl.POST, 1)
		conn.setopt(pycurl.COOKIE, cookie_file_name)
		conn.setopt(pycurl.POSTFIELDS, login_form_data)
		conn.setopt(pycurl.WRITEFUNCTION, b.write)
		conn.perform()
		output = unicode(b.getvalue(), 'utf-8', 'ignore')

		# in case there are no announcements for the specific lesson
		if not (BeautifulSoup(output).find('p', 'alert1')):
			soup1 = BeautifulSoup(output).find('table')

			j = 0
			k = 1
			
			for item in soup1.findAll('small'):
				main_text = ''
				unique = ''
				name = ''
				title = ''

				l = 0

				# in case there is another table/td inside the announcement OR there is no content
				try:
					for item1 in soup1.findAll('td')[k].contents:
						main_text += str(soup1.findAll('td')[k].contents[l])
						l += 1
					main_text = p.sub(' ', main_text).strip()
					main_text = ''.join(main_text.split(')')[1:])
				except IndexError:
					pass

				# in case there is no title
				try:
					if (len(str(soup1.findAll('td')[k].b)) > 8):
						name = soup1.findAll('td')[k].b.contents[0].strip()
					else: 
						name = 'No Title'
				except IndexError:
					pass

				if (main_text == ''):
					unique = name
				else:
					unique = main_text

					eclass_teilar_gr = Announcements(
						title = name,
						urlid = geteclassid(cid),
						description = main_text,
						unique = unique,
						url = link,
						attachment_url = '',
						attachment_text = ''
					)

				try:
					eclass_teilar_gr.save()
				except MySQLdb.IntegrityError:
					pass

				j += 1
				k += 2

	i += 1

### noc.teilar.gr ###

b = StringIO.StringIO()
conn.setopt(pycurl.URL, 'http://noc-portal.teilar.gr/index.php?option=com_content&task=category&sectionid=1&id=29&Itemid=89')
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = (b.getvalue()).decode('windows-1253')
soup = BeautifulSoup(output)

for i in xrange(2):
	for j in xrange(5):
		link = str(soup.findAll('tr', 'sectiontableentry' + str(i + 1))[j].contents[1].contents[1]).split('"')[1].replace('&amp;', '&')
		
		b = StringIO.StringIO()
		conn.setopt(pycurl.URL, link)
		conn.setopt(pycurl.WRITEFUNCTION, b.write)
		conn.perform()
		output = (b.getvalue()).decode('windows-1253')
		soup1 = BeautifulSoup(output)

		main_text = str(soup1.findAll('table', 'contentpaneopen')[1])
		main_text = p.sub(' ', main_text)

		noc_teilar_gr = Announcements(
			title = str(soup.findAll('tr', 'sectiontableentry' + str(i + 1))[j].contents[1].contents[1].contents[0]).strip(),
			url = link,
			unique = link,
			urlid = getid('cid', 50),
			description = main_text.strip(),
			attachment_text = '',
			attachment_url = '',
		)

		try:
			noc_teilar_gr.save()
		except MySQLdb.IntegrityError:
			pass

### www.career.teilar.gr ###

b = StringIO.StringIO()
conn.setopt(pycurl.URL, 'http://www.career.teilar.gr/newslist.php')
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = unicode(b.getvalue(), 'utf-8', 'ignore')
soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[5]))

for i in xrange(20):
	link = 'http://www.career.teilar.gr/' + str(soup.findAll('a')[i]).split('"')[1]

	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, link)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup1 = BeautifulSoup(output)

	main_text = ''

	main_text = str(soup1.findAll('table')[5])
	main_text = p.sub(' ', main_text)

	career_teilar_gr = Announcements(
		title = str(soup.findAll('a')[i].contents[0]),
		url = link,
		unique = link,
		urlid = getid('cid', 51),
		description = main_text.strip(),
		attachment_text = '',
		attachment_url = '',
	)

	try:
		career_teilar_gr.save()
	except MySQLdb.IntegrityError:
		pass

### linuxteam.cs.teilar.gr ###

b = StringIO.StringIO()
conn.setopt(pycurl.URL, 'http://linuxteam.cs.teilar.gr')
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = b.getvalue()
soup = BeautifulSoup(str(BeautifulSoup(output).findAll('h2', 'title')))

for i in range(4, 7):
	link = 'http://linuxteam.cs.teilar.gr' + str(soup.findAll('h2', 'title')[i].contents[0]).split('"')[1]

	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, link)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = b.getvalue()
	soup1 = BeautifulSoup(output)

	main_text = ''

	main_text = str(soup1.findAll('div', 'content')[4].contents[0])
	main_text = p.sub(' ', main_text)

	linuxteam = Announcements(
		title = str(soup.findAll('h2', 'title')[i].contents[0].contents[0]),
		url = link,
		unique = link,
		urlid = getid('cid', 52),
		description = main_text.strip(),
		attachment_text = '',
		attachment_url = '',
	)

	try:
		linuxteam.save()
	except MySQLdb.IntegrityError:
		pass

### dionysos.teilar.gr ###

link = 'http://dionysos.teilar.gr/Menu/r1.htm'

b = StringIO.StringIO()
conn.setopt(pycurl.URL, link)
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = (b.getvalue()).decode('windows-1253')
soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[1]))

for i in xrange(len(soup.findAll('th')) - 1):
	main_text = ''
	for j in xrange(len(soup.findAll('th')[i+1].b.contents)):
		main_text += str(soup.findAll('th')[i+1].b.contents[j])
	main_text = p.sub(' ', main_text)

	dionysos = Announcements(
		title = 'No Title',
		url = link,
		urlid = getid('cid', 53),
		description = main_text.strip(),
		unique = 'dionysos' + main_text.strip(),
		attachment_url = '',
		attachment_text = '',
	)

	try:
		dionysos.save()
	except MySQLdb.IntegrityError:
		pass

### library.teilar.gr ###

b = StringIO.StringIO()
conn.setopt(pycurl.URL, 'http://library.teilar.gr/news_gr.php')
conn.setopt(pycurl.WRITEFUNCTION, b.write)
conn.perform()
output = unicode(b.getvalue(), 'utf-8', 'ignore')
soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[9]))

for item in soup.findAll('a', 'BlackText11'):
	title = item.contents[0]
	link = 'http://library.teilar.gr/' +str(item).split('"')[1]

	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, link)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup1 = BeautifulSoup(output)
	main_text = soup1.findAll('td', 'BlackText11')[2].contents[0]
	main_text = p.sub(' ', main_text)
	
	library = Announcements(
		title = title,
		url = link,
		urlid = getid('cid', 54),
		description = main_text.strip(),
		unique = link,
		attachment_url = '',
		attachment_text = '',
	)

	try:
		library.save()
	except MySQLdb.IntegrityError:
		pass

### www.pr.teilar.gr ###

link = ['general_news/', 'meeting_conference/']

for item in link:
	b = StringIO.StringIO()
	conn.setopt(pycurl.URL, 'http://www.pr.teilar.gr/el/announcements/' + item)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output)

	for i in xrange(len(soup.findAll('span','ba'))):
		title = soup.findAll('span', 'ba')[i].a.contents[0]
		link1 = 'http://www.pr.teilar.gr' + str(soup.findAll('span', 'ba')[i].contents[0]).split('"')[1]
		
		b = StringIO.StringIO()
		conn.setopt(pycurl.URL, link1)
		conn.setopt(pycurl.WRITEFUNCTION, b.write)
		conn.perform()
		output = unicode(b.getvalue(), 'utf-8', 'ignore')
		soup1 = BeautifulSoup(output)

		main_text = ''
		for j in xrange(len(soup1.findAll('td', 'subject')[0].contents)):
			main_text += str(soup1.findAll('td', 'subject')[0].contents[j])
		main_text = p.sub(' ', main_text)

		pr = Announcements(
			title = title,
			url = link1,
			urlid = getid('cid', 55),
			description = main_text,
			unique = link1,
			attachment_url = '',
			attachment_text = '',
		)

		try:
			pr.save()
		except MySQLdb.IntegrityError:
			pass
