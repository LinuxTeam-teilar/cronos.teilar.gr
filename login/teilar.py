# -*- coding: utf-8 -*-

def dionysos_login(link, username, password):
	import pycurl
	import StringIO
	import urllib
	import os
	import urlparse

	conn = pycurl.Curl()
	b = StringIO.StringIO()
	
	if link == 0:
		cookie_file_name = os.tempnam('/tmp','dionysos')
		login_form_seq = [
			('userName', username),
			('pwd', password),
			('submit1', '%C5%DF%F3%EF%E4%EF%F2'),
			('loginTrue', 'login')
		]
		login_form_data = urllib.urlencode(login_form_seq)
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
		return (b.getvalue()).decode('windows-1253')
	print 'eimai e3o'
	conn.setopt(pycurl.URL, link)
	conn.setopt(pycurl.POST, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.COOKIE, cookie_file_name)
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	return (b.getvalue()).decode('windows-1253')

def eclass_login(username, password):
	import pycurl
	import StringIO
	import urllib
	import os
	import urlparse
	
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	login_form_seq = [
		('uname', username),
		('pass', password),
		('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82')
	]
	login_form_data = urllib.urlencode(login_form_seq)
	conn.setopt(pycurl.FOLLOWLOCATION, 1)
	conn.setopt(pycurl.POSTFIELDS, login_form_data)
	conn.setopt(pycurl.URL, 'http://e-class.teilar.gr/index.php')
	conn.setopt(pycurl.WRITEFUNCTION, b.write)
	conn.perform()
	return unicode(b.getvalue(), 'utf-8', 'ignore')

def webmail_login(link, username, password):
	import pycurl
	import StringIO
	import urllib
	import os
	import urlparse
	
	b = StringIO.StringIO()
	conn = pycurl.Curl()
	cookie_file_name = os.tempnam('/tmp','webmail')
	login_form_seq = [
		('login_username', username),
		('secretkey', password),
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
	if link == 0:
		return
	conn.setopt(pycurl.URL, link)
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php')
	#conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX')
	conn.perform()
	return (b.getvalue()).decode('iso-8859-7')
