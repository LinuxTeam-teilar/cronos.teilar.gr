# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import urllib
import os
import tempfile
import urlparse

def dionysos_login(link, username, password):
    conn = pycurl.Curl()
    b = StringIO.StringIO()

    fd, cookie_path = tempfile.mkstemp(prefix='dionysos_', dir='/tmp')
    login_form_seq = [
        ('userName', username),
        ('pwd', password),
        ('submit1', '%C5%DF%F3%EF%E4%EF%F2'),
        ('loginTrue', 'login')
    ]
    login_form_data = urllib.urlencode(login_form_seq)
    conn.setopt(pycurl.FOLLOWLOCATION, 1)
    conn.setopt(pycurl.COOKIEFILE, cookie_path)
    conn.setopt(pycurl.COOKIEJAR, cookie_path)
    conn.setopt(pycurl.URL, 'https://dionysos.teilar.gr/unistudent/')
    conn.setopt(pycurl.POST, 0)
    conn.perform()
    conn.setopt(pycurl.URL, 'https://dionysos.teilar.gr/unistudent/login.asp')
    conn.setopt(pycurl.POST, 1)
    conn.setopt(pycurl.POSTFIELDS, login_form_data)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    if link == 0:
        soup = BeautifulSoup((b.getvalue()).decode('windows-1253'))
        try:
            soup.find('td', 'whiteheader').b.contents[0] == u'Είσοδος Φοιτητή'
            os.close(fd)
            os.remove(cookie_path)
            return 1
        except:
            return (b.getvalue()).decode('windows-1253')
    else:
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, link)
        conn.setopt(pycurl.POST, 1)
        conn.setopt(pycurl.POSTFIELDS, login_form_data)
        conn.setopt(pycurl.COOKIE, cookie_path)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        os.close(fd)
        os.remove(cookie_path)
        return (b.getvalue()).decode('windows-1253')

def eclass_login(username, password):
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
    soup = BeautifulSoup(unicode(b.getvalue(), 'utf-8', 'ignore'))
    try:
        if soup.find('div', 'user').contents[0] == '&nbsp;':
            return 1
        else:
            raise
    except:
        return unicode(b.getvalue(), 'utf-8', 'ignore')

def webmail_login(link, username, password):
    b = StringIO.StringIO()
    conn = pycurl.Curl()
    fd, cookie_path = tempfile.mkstemp(prefix='dionysos_', dir='/tmp'
    login_form_seq = [
        ('login_username', username),
        ('secretkey', password),
        ('js_autodetect_results', '1'),
        ('just_logged_in', '1')
    ]
    login_form_data = urllib.urlencode(login_form_seq)
    conn.setopt(pycurl.FOLLOWLOCATION, 0)
    conn.setopt(pycurl.COOKIEFILE, cookie_path)
    conn.setopt(pycurl.COOKIEJAR, cookie_path)
    conn.setopt(pycurl.URL, 'http://myweb.teilar.gr')
    conn.setopt(pycurl.POST, 0)
    conn.perform()
    conn.setopt(pycurl.URL, 'http://myweb.teilar.gr/src/redirect.php')
    conn.setopt(pycurl.POST, 1)
    conn.setopt(pycurl.POSTFIELDS, login_form_data)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    soup = BeautifulSoup(b.getvalue().decode('iso-8859-7'))
    try:
        if soup.title.contents[0].split('-')[2].strip() == 'Άγνωστος χρήστης η εσφαλμένος κωδικός.':
            return 1
    except:
        if link == 0:
            return (b.getvalue()).decode('iso-8859-7')
        conn.setopt(pycurl.URL, link)
        conn.perform()
        os.close(fd)
        os.remove(cookie_path)
        return (b.getvalue()).decode('iso-8859-7')
