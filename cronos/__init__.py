# -*- coding: utf-8 -*-

from cronos.common.exceptions import CronosError, LoginError
from cronos.common.log import log_extra_data
from bs4 import BeautifulSoup
import logging
import requests
import sys

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_package_version():
    return '0.3-dev'

__version__ = get_package_version()

class Cronos(object):
    def __init__(self, dionysos_username, dionysos_password, eclass_username = None, eclass_password = None):
        self.dionysos_username = dionysos_username
        self.dionysos_password = dionysos_password
        self.dionysos_index_output = None
        self.dionysos_index_minimal_output = None
        self.dionysos_declaration_output = None
        self.dionysos_grades_output = None
        self.eclass_username = eclass_username
        self.eclass_password = eclass_password
        self.eclass_output = None

    def dionysos_auth_login(self, request = None, personal_data = False, declaration = False, grades = False):
        '''
        Authentication to dionysos.teilar.gr
        '''
        dionysos_session = requests.session()
        '''
        The data that will be sent to the login form of dionysos.teilar.gr
        '''
        login_data = {
            'userName': self.dionysos_username,
            'pwd': self.dionysos_password,
            'submit1': '%C5%DF%F3%EF%E4%EF%F2',
            'loginTrue': 'login'
        }
        dionysos_login_url = 'https://dionysos.teilar.gr/unistudent/'
        try:
            '''
            Send a GET request to get the cookies. If it fails then dionysos.teilar.gr is down
            '''
            response = dionysos_session.get(dionysos_login_url)
            response.encoding = 'windows-1253'
        except Exception as warning:
            if request:
                logger_syslog.warning(warning, extra = log_extra_data(request))
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
        soup = BeautifulSoup(response.text)
        try:
            temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
            '''
            Check if the resulting HTML output is the expected one. If not, then
            dionysos.teilar.gr is malfunctioning.
            '''
            if temp_td_whiteheader != u'Είσοδος Φοιτητή':
                raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
        except AttributeError:
            pass
        '''
        If everything was fine so far, then dionysos.teilar.gr is up and running.
        Now we can proceed to the actual authentication.
        '''
        response = dionysos_session.post(dionysos_login_url, login_data)
        if personal_data:
            response.encoding = 'windows-1253'
            soup = BeautifulSoup(response.text)
            try:
                '''
                Check if the credentials are correct
                '''
                temp_td_whiteheader = soup.find('td', 'whiteheader').b.contents[0]
                if temp_td_whiteheader == u'Είσοδος Φοιτητή':
                    '''
                    The resulting HTML output still contains the login form, which
                    means that the authentication failed
                    '''
                    raise LoginError
            except AttributeError:
                pass
            '''
            Authentication succeeded, get the full HTML output and a small piece
            of it in a different var for caching reasons
            '''
            self.dionysos_index_output = response.text
            self.dionysos_index_minimal_output = soup.find_all('table')[14].find_all('tr')
        if declaration:
            '''
            Get the HTML output of the declaration page
            '''
            dionysos_declaration_url = 'https://dionysos.teilar.gr/unistudent/stud_NewClass.asp?studPg=1&mnuid=diloseis;newDil&'
            response = dionysos_session.get(dionysos_declaration_url)
            response.encoding = 'windows-1253'
            self.dionysos_declaration_output = response.text
        if grades:
            '''
            Get the HTML output of the grades page
            '''
            dionysos_grades_url = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
            response = dionysos_session.get(dionysos_grades_url)
            response.encoding = 'windows-1253'
            self.dionysos_grades_output = response.text

    def get_dionysos_last_name(self, request = None):
        '''
        Retrieves student's last name from dionysos.teilar.gr
        '''
        if not self.dionysos_index_minimal_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            self.dionysos_last_name = unicode(self.dionysos_index_minimal_output[5].find_all('td')[1].contents[0])
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης επωνύμου')

    def get_dionysos_first_name(self, request = None):
        '''
        Retrieves student's first name from dionysos.teilar.gr
        '''
        if not self.dionysos_index_minimal_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            self.dionysos_first_name = self.dionysos_index_minimal_output[6].find_all('td')[1].contents[0]
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Ονόματος')

    def get_dionysos_registration_number(self, request = None):
        '''
        Retrieves student's registration number from dionysos.teilar.gr
        '''
        if not self.dionysos_index_minimal_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            self.dionysos_registration_number = self.dionysos_index_minimal_output[7].find_all('td')[1].contents[0]
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Αριθμού Μητρώου')

    def get_dionysos_school(self, request = None):
        '''
        Retrieves student's school from dionysos.teilar.gr
        '''
        if not self.dionysos_index_minimal_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            self.dionysos_school = self.dionysos_index_minimal_output[8].find_all('td')[1].contents[0].strip()
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Σχολής')

    def get_dionysos_semester(self, request = None):
        '''
        Retrieves student's semester from dionysos.teilar.gr
        '''
        if not self.dionysos_index_minimal_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            self.dionysos_semester = self.dionysos_index_minimal_output[9].find_all('td')[1].contents[0]
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Εξαμήνου')

    def get_dionysos_introduction_year(self, request = None):
        '''
        Retrieves student's introduction year from dionysos.teilar.gr
        '''
        if not self.dionysos_index_output:
            self.dionysos_auth_login(request, personal_data = True)
        try:
            soup = BeautifulSoup(self.dionysos_index_output).find_all('table')[15]
            '''
            Introduction is in the following form:
            2004 - 2005 X or 2004 - 2005 E
            first_year - second_year season
            We need it in the form 2004X (YearSeason):
            if season is 'X', then year is first_year (2004X)
            if season is 'E', then year is second_year (2005E)
            '''
            season = unicode(soup.find_all('span','tablecell')[1].contents[0])[0]
            if season == u'Ε':
                year = unicode(soup.find_all('span','tablecell')[0].contents[0].split('-')[1])
            else:
                year = unicode(soup.find_all('span','tablecell')[0].contents[0].split('-')[0])
            self.dionysos_introduction_year =  year + season
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Έτους Εισαγωγής')

    def get_dionysos_declaration(self, request = None):
        '''
        Retrieves student's latest declaration
        '''

        '''
        Declaration includes the following information:
        Lesson code eg 121E
        Title eg ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ Ι (Θ)
        Semester eg Β
        DM eg 2
        Hours eg 4
        Type eg Y
        '''
        if not self.dionysos_declaration_output:
            self.dionysos_auth_login(declaration = True)
        soup = BeautifulSoup(self.dionysos_declaration_output)
        '''
        Temp variables are named based on the HTML tags they contain. Those
        variables give faster results, since we don't have to regenerate the
        same data in each time the for loop is executed.
        '''
        temp = soup.find_all('table')[15]
        temp_td = temp.find_all('td')
        temp_span_underline = temp.find_all('span', 'underline')
        '''
        The lessons are stored in a dictionary with the following structure:
        {lcode: [title, semester, dm, hours, type]}
        '''
        declaration = {}
        i = 8
        for item in temp_span_underline:
            lcode = temp_td[i].contents[2].strip()[1:-1]
            title = item.contents[0].strip()
            semester = temp_td[i+2].contents[0]
            dm = temp_td[i+3].contents[0]
            hours = temp_td[i+4].contents[0]
            ltype = temp_td[i+5].contents[0]
            i +=7
            declaration[lcode] = [title, semester, dm ,hours, ltype]
        '''
        Get total lessons, total DMs and total hours, and add them
        in the declaration dictionary as well
        '''
        totals = soup.find_all('td', 'error')
        declaration['totals'] = []
        for item in totals:
            declaration['totals'].append(item.contents[0])
        self.dionysos_declaration = declaration

    def get_dionysos_grades(self, request = None):
        self.dionysos_grades = None

    def get_dionysos_account(self, request = None):
        '''
        Return the full dionysos profile
        '''
        # TODO: return it in json format
        try:
            self.get_dionysos_last_name(request)
            self.get_dionysos_first_name(request)
            self.get_dionysos_registration_number(request)
            self.get_dionysos_school(request)
            self.get_dionysos_semester(request)
            self.get_dionysos_introduction_year(request)
            self.get_dionysos_declaration(request)
            self.get_dionysos_grades(request)
        except (CronosError, LoginError) as error:
            if request:
                raise
            else:
                sys.stdout.write( '%s\n' % error)

    def eclass_auth_login(self, request = None):
        '''
        Authentication to e-class.teilar.gr
        '''
        eclass_session = requests.session()
        login_data = {
            'uname': self.eclass_username,
            'pass': self.eclass_password,
            'submit': 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82',
        }
        '''
        Send a GET request to get the cookies. If it fails then e-class.teilar.gr is down
        '''
        eclass_session.get('http://openclass.teilar.gr')
        try:
            response = eclass_session.get('http://openclass.teilar.gr')
        except Exception as warning:
            if request:
                logger_syslog.warning(warning, extra = log_extra_data(request))
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το openclass.teilar.gr')
        '''
        Proceed to actual authentication
        '''
        response = eclass_session.post('http://openclass.teilar.gr', login_data)
        '''
        Check if the login is successful
        '''
        try:
            soup = BeautifulSoup(response.text).find_all('p', 'alert1')[0]
            if soup.contents[0] == u'Λάθος στοιχεία.':
                raise LoginError
        except AttributeError:
            pass
        self.eclass_output = response.text

    def get_eclass_lessons(self, request = None):
        '''
        Get eclass lessons
        '''
        if not self.eclass_output:
            self.eclass_auth_login(request)
        try:
            eclass_lessons = {}
            all_lessons = BeautifulSoup(self.eclass_output).find('table', 'tbl_lesson').find_all('td', align='left')
            for item in all_lessons:
                lcode = item.span.contents[0][1:-1]
                url = u'http://openclass.teilar.gr/courses/%s/' % lcode
                name = item.a.contents[0]
                # TODO: teacher, faculty, ltype
                eclass_lessons[lcode] = [url, name]
            self.eclass_lessons = eclass_lessons
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης μαθημάτων e-class')

    def get_eclass_account(self, request = None):
        '''
        Get the full eclass profile
        '''
        # TODO: Return it in JSON format
        try:
            self.get_eclass_lessons(request)
        except (CronosError, LoginError) as error:
            sys.stdout.write( '%s\n' % error)
