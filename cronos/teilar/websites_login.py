# -*- coding: utf-8 -*-

from cronos import CronosError, log_extra_data
from bs4 import BeautifulSoup
import logging
import pycurl
import StringIO
import urllib
import os
import tempfile
import urlparse
import urllib2

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def teilar_login(url = None):
    '''
    Try to connect to *.teilar.gr and get the resulting HTML output.
    '''
    try:
        site = urllib2.urlopen(url)
        output = site.read()
    except Exception as error:
        '''
        *.teilar.gr is down
        '''
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        site = url.split('/')[2]
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το %s' % site)
    return unicode(output, 'utf-8', 'ignore')

def dionysos_login(username, password, url = None, request = None):
    '''
    Try to connect to dionysos.teilar.gr and get the resulting HTML output.
    If URL is None, then an authentication attempt is also performed. In order
    to verify if the authentication succeeded, we parse the final HTML output
    and check if it still contains the login form
    '''
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    fd, cookie_path = tempfile.mkstemp(prefix='dionysos_', dir='/tmp')
    '''
    The data that will be sent to the login form of dionysos.teilar.gr
    '''
    login_form_seq = [
        ('userName', username),
        ('pwd', password),
        ('submit1', '%C5%DF%F3%EF%E4%EF%F2'),
        ('loginTrue', 'login')
    ]
    login_form_data = urllib.urlencode(login_form_seq)
    '''
    We need to perform two connections. I'm not sure yet why, probably because
    the cookie needs to get initialized and then to be actually used.
    '''
    conn.setopt(pycurl.FOLLOWLOCATION, 1)
    conn.setopt(pycurl.COOKIEFILE, cookie_path)
    conn.setopt(pycurl.COOKIEJAR, cookie_path)
    conn.setopt(pycurl.URL, 'https://dionysos.teilar.gr/unistudent/')
    conn.setopt(pycurl.POST, 0)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    try:
        '''
        Perform a connection, if it fails then dionysos.teilar.gr is down
        '''
        conn.perform()
    except Exception as error:
        os.close(fd)
        os.remove(cookie_path)
        logger_syslog.warning(error, extra = log_extra_data(username, request))
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
    soup = BeautifulSoup(b.getvalue().decode('windows-1253'))
    try:
        temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
        '''
        Check if the resulting HTML output is the expected one. If not, then
        dionysos.teilar.gr is malfunctioning.
        '''
        if temp_td_whiteheader != u'Είσοδος Φοιτητή':
            raise
    except Exception as error:
        os.close(fd)
        os.remove(cookie_path)
        logger_syslog.warning(error, extra = log_extra_data(username, request))
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
    '''
    If everything was fine so far, then dionysos.teilar.gr is up and running.
    Now we can proceed to the actual authentication.
    '''
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'https://dionysos.teilar.gr/unistudent/login.asp')
    conn.setopt(pycurl.POST, 1)
    conn.setopt(pycurl.POSTFIELDS, login_form_data)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    if not url:
        '''
        Checking if the credentials are correct
        '''
        soup = BeautifulSoup(b.getvalue().decode('windows-1253'))
        try:
            temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
            if temp_td_whiteheader == u'Είσοδος Φοιτητή':
                '''
                The resulting HTML output still contains the login form, which means
                that the authentication failed.
                '''
                os.close(fd)
                os.remove(cookie_path)
                return
        except (NameError, AttributeError):
            pass
    else:
        '''
        Connect to the requested URL and return the HTML output
        '''
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, url)
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

def webmail_login(url, username, password):
    b = StringIO.StringIO()
    conn = pycurl.Curl()
    fd, cookie_path = tempfile.mkstemp(prefix='webmail_', dir='/tmp')
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
        if url == 0:
            return (b.getvalue()).decode('iso-8859-7')
        conn.setopt(pycurl.URL, url)
        conn.perform()
        os.close(fd)
        os.remove(cookie_path)
        return (b.getvalue()).decode('iso-8859-7')
