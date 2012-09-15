# -*- coding: utf-8 -*-

from cronos.common.log import CronosError, log_extra_data
from bs4 import BeautifulSoup
import logging
import requests

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_package_version():
    return '0.3-dev'

__version__ = get_package_version()

def teilar_anon_login(url = None):
    '''
    Try to connect to *.teilar.gr and get the resulting HTML output.
    '''
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
    except Exception as error:
        '''
        *.teilar.gr is down
        '''
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        site = url.split('/')[2]
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το %s' % site)
    return response.text

def dionysos_auth_login(username, password, url = None, request = None):
    '''
    Try to connect to dionysos.teilar.gr and get the resulting HTML output.
    If URL is None, then an authentication attempt is also performed. In order
    to verify if the authentication succeeded, we parse the final HTML output
    and check if it still contains the login form
    '''
    dionysos_session = requests.session()
    '''
    The data that will be sent to the login form of dionysos.teilar.gr
    '''
    login_data = {
        'userName': username,
        'pwd': password,
        'submit1': '%C5%DF%F3%EF%E4%EF%F2',
        'loginTrue': 'login'
    }
    '''
    We need to perform two connections. I'm not sure yet why, probably because
    the cookie needs to get initialized and then to be actually used.
    '''
    try:
        '''
        Perform a connection with fake data. If it fails then dionysos.teilar.gr is down
        '''
        response = dionysos_session.post('https://dionysos.teilar.gr/unistudent/', {'username': 'test'})
        response.encoding = 'windows-1253'
    except Exception as error:
        logger_syslog.warning(error, extra = log_extra_data(username, request))
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
    soup = BeautifulSoup(response.text)
    try:
        temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
        '''
        Check if the resulting HTML output is the expected one. If not, then
        dionysos.teilar.gr is malfunctioning.
        '''
        if temp_td_whiteheader != u'Είσοδος Φοιτητή':
            raise
    except Exception as error:
        logger_syslog.warning(error, extra = log_extra_data(username, request))
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
    '''
    If everything was fine so far, then dionysos.teilar.gr is up and running.
    Now we can proceed to the actual authentication.
    '''
    response = dionysos_session.post('https://dionysos.teilar.gr/unistudent/', login_data)
    response.encoding = 'windows-1253'
    if not url:
        '''
        Checking if the credentials are correct
        '''
        soup = BeautifulSoup(response.text)
        try:
            temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
            if temp_td_whiteheader == u'Είσοδος Φοιτητή':
                '''
                The resulting HTML output still contains the login form, which means
                that the authentication failed.
                '''
                return
        except (NameError, AttributeError):
            pass
    else:
        '''
        Connect to the requested URL and return the HTML output
        '''
        response = dionysos_session.get(url)
        response.encoding = 'windows-1253'
    return response.text

def eclass_auth_login(username, password, request = None):
    '''
    Authentication to eclass
    '''
    eclass_session = requests.session()
    login_data = {
        'uname': username,
        'pass': password,
        'submit': 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82',
    }
    '''
    Check if eclass is up
    '''
    response = eclass_session.post('http://openclass.teilar.gr', login_data)
    try:
        response = eclass_session.post('http://openclass.teilar.gr', login_data)
    except Exception as error:
        logger_syslog.warning(error, extra = log_extra_data(username, request))
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το openclass.teilar.gr')
    '''
    Check if the login is successful
    '''
    try:
        soup = BeautifulSoup(response.text).find_all('p', 'alert1')[0]
        if soup.contents[0] == u'Λάθος στοιχεία.':
            return
    except:
        pass
    return response.text
