# -*- coding: utf-8 -*-

from proj_root import *
import os
import sys
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from BeautifulSoup import BeautifulSoup
from cronos.announcements.models import *
from django.conf import settings
from django.db.utils import IntegrityError
import MySQLdb
import pycurl
import re
import StringIO
import tempfile
import urllib
import urlparse

conn = pycurl.Curl()
p = re.compile(r'<[^<]*?/?>')

def www_teilar_gr():
	for cid in xrange(30):
		b = StringIO.StringIO()
		conn.setopt(pycurl.URL, 'http://www.teilar.gr/tmimatanews.php?cid=' + str(cid))
		conn.setopt(pycurl.WRITEFUNCTION, b.write)
		conn.perform()
		output = unicode(b.getvalue(), 'utf-8', 'ignore')
		soup = BeautifulSoup(output)

		school = str(soup.findAll('td', 'BlueTextBold')[0])
		school = p.sub(' ', school)

		if (cid == 0):
			school = 'Κεντρική Σελίδα ΤΕΙ Λάρισας'
		if (cid == 2):
			school = 'Τμήμα Τεχνολογίας Πληροφορικής και Τηλεπικοινωνιών'
		if (len(school) > 5):
			depart = Id(
				urlid = 'cid' + str(cid),
				name = school.strip(),
				department = '',
				email = '',
			)
			try:
				depart.save()
				print 'ADDED ' + school
			except IntegrityError:
				pass
			except Exception as error:
				print 'ERROR: ' + school.strip() 
				print 'ERROR: ' + str(error)
				pass

def extra_sites():
	dest = [
		['noc', 'Κέντρο Διαχείρισης Δικτύου'],
		['career', 'Γραφείο Διασύνδεσης'],
		['linuxteam', 'Linux Team'],
		['dionysos', 'Πρόγραμμα Γραμματείας'],
		['library', 'Κεντρική Βιβλιοθήκη'],
		['pr', 'Γραφείο Δημοσίων και Διεθνών Σχέσεων'],
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
			print 'ADDED ' + str(dest[i][1])
		except IntegrityError:
			pass
		except Exception as error:
			print 'ERROR: ' + str(dest[i][1]) 
			print 'ERROR: ' + str(error)
			pass

def professors():
	for pid in xrange(400):
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
			teacher = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11Bold')[1].contents[0]))).strip()
		except IndexError:
			pass
		try:
			email = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11')[5])).a.contents[0])
		except AttributeError:
			try:
				email = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11')[5].contents[0])))
			except IndexError:
				pass
		except IndexError:
			pass
		try:
			depart = str(BeautifulSoup(str(soup.findAll('td', 'BlackText11')[2]))).strip()
			depart = p.sub('',depart)
			if depart.split(' ')[1] == 'Τεχν.':
				depart = 'Τμήμα Τεχνολογίας ' + ' '.join(depart.split(' ')[2:])
		except IndexError:
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
				print 'ADDED ' + teacher
			except IntegrityError:
				pass
			except Exception as error:
				print 'ERROR: ' + teacher 
				print 'ERROR: ' + str(error)
				pass


def eclass_teilar_gr():
	b = StringIO.StringIO()
	fd, cookie_path = tempfile.mkstemp(prefix='eclass_', dir='/tmp')
	login_form_seq = [
		('uname', settings.ECLASS_USER),
		('pass', settings.ECLASS_PASSWORD),
		('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82')
	]
	login_form_data = urllib.urlencode(login_form_seq)
	conn.setopt(pycurl.FOLLOWLOCATION, 1)
	conn.setopt(pycurl.COOKIEFILE, cookie_path)
	conn.setopt(pycurl.COOKIEJAR, cookie_path)
	conn.setopt(pycurl.URL, 'http://openclass.teilar.gr/index.php')
	conn.setopt(pycurl.POST, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	output = unicode(b.getvalue(), 'utf-8', 'ignore')
	soup = BeautifulSoup(output).find('table', 'FormData')

	i = 0

	lessonslist = soup.findAll('a')
	for item in lessonslist:
		if (i%2 == 0):
			cid = str(soup.findAll('a')[i].contents[0]).split('-')[0]
			lesson = ''
			for j in xrange(len((soup.findAll('a')[i].contents[0]).split('-')) - 1):
				lesson += str(soup.findAll('a')[i].contents[0]).split('-')[j+1].strip() + ' '

			eclass = Id(
				urlid = str(cid),
				name = lesson.strip(),
				department = '',
				email = '',
			)
			try:
				eclass.save()
				print 'ADDED ' + lesson.strip()
			except IntegrityError:
				pass
			except MySQLdb.Warning, warning:
				print 'ADDED ' + lesson.strip()
				print 'WARNING: ' + str(warning)
				pass
			except Exception as error:
				print 'ERROR: ' + lesson.strip() 
				print 'ERROR: ' + str(error)
				pass
		i += 1
	os.close(fd)
	os.remove(cookie_path)

def main():
	www_teilar_gr()
	extra_sites()
	professors()
	eclass_teilar_gr()
	print "DONE"

if __name__ == "__main__":
	main()
