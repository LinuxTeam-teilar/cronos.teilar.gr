# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from cronos.common.exceptions import CronosError, LoginError
from cronos.common.log import log_extra_data
import logging
import requests
import sys

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_package_version():
    return '0.3'

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
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το dionysos.teilar.gr')
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
            dionysos_declaration_url = 'https://dionysos.teilar.gr/unistudent/stud_vClasses.asp?studPg=1&mnuid=diloseis;showDil&'
            response = dionysos_session.get(dionysos_declaration_url)
            response.encoding = 'windows-1253'
            self.dionysos_declaration_output = response.text
        if grades:
            '''
            Get the HTML output of the grades page
            '''
            dionysos_grades_url = 'https://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
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
        Grade
        '''
        if not self.dionysos_declaration_output:
            self.dionysos_auth_login(declaration = True)
        soup = BeautifulSoup(self.dionysos_declaration_output)
        '''
        Temp variables are named based on the HTML tags they contain. Those
        variables give faster results, since we don't have to regenerate the
        same data in each time the for loop is executed.
        '''
        try:
            temp = soup.find_all('table')[13].find('table')
            temp_td_bottom = temp.find_all('td', 'bottomborderLight')
            declaration = temp_td_bottom
            i = 0
            while i < len(declaration):
                '''
                Some of the above results are inside single HTML tags (<td>2</td>)
                and some are in double ones (<td><span>4</span</td>). We work around
                this with a try/except block
                '''
                try:
                    '''
                    Add information that is inside double HTML tags
                    '''
                    declaration[i] = unicode(declaration[i].contents[0].contents[0]).strip()
                except AttributeError:
                    '''
                    Add information that is inside single HTML tags
                    '''
                    declaration[i] = unicode(declaration[i].contents[0]).strip()
                i += 1
            declaration = ':'.join(declaration).replace('&amp;', '&')
            self.dionysos_declaration = declaration
        except Exception as error:
            if request:
                logger_syslog.error(error, extra = log_extra_data(request))
                logger_mail.exception(error)
            raise CronosError(u'Αδυναμία ανάκτησης Δήλωσης')

    def get_dionysos_grades(self, request = None):
        '''
        Retrieves student's grades
        '''
        if not self.dionysos_grades_output:
            self.dionysos_auth_login(grades = True)
        soup = BeautifulSoup(self.dionysos_grades_output)
        grades = ''
        i = 0
        item = soup.find_all('table')[13].find_all('td')
        length_all_td = len(item)
        semesters = soup.find_all('table')[13].find_all('td', 'groupHeader')
        lessons = soup.find_all('table')[13].find_all('td', 'topBorderLight')
        while i < length_all_td:
            item0 = item[i]
            if item0 in semesters:
                grades += item0.contents[0] + ','
            if item0 in lessons:
                year = item[i+6].contents[0].i.contents[0].strip()
                year = year[:10].strip() + year[-9:].strip()
                grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                    item0.contents[0].strip(),
                    item[i+1].contents[0].strip(),
                    item[i+2].contents[0].strip(),
                    item[i+3].contents[0].strip(),
                    item[i+4].contents[0].strip(),
                    item[i+5].span.contents[0].replace(',', '.').strip(),
                    year.replace('--', '-'),
                )
                try:
                    if item[i+9].contents[1].strip()[4] in [u'Θ', u'Ε']:
                        year = item[i+14].contents[0].i.contents[0].strip()
                        year = year[:10].strip() + year[-9:]
                        grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                            item[i+9].contents[1].strip(),
                            '',
                            item[i+10].i.contents[0].strip(),
                            item[i+11].contents[0].strip(),
                            item[i+12].contents[0].strip(),
                            item[i+13].contents[0].replace(',', '.').strip(),
                            year.replace('--', '-'),
                        )
                        year = item[i+22].contents[0].i.contents[0]
                        year = year[:10].strip() + year[-9:]
                        grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                            item[i+17].contents[1].strip(),
                            '',
                            item[i+18].i.contents[0].strip(),
                            item[i+19].contents[0].strip(),
                            item[i+20].contents[0].strip(),
                            item[i+21].contents[0].replace(',', '.').strip(),
                            year.replace('--', '-'),
                        )
                        i += 11
                except:
                    pass
                i += 6
            try:
                if item0.contents[0][:6] == u'Σύνολα':
                    grades += '%s,%s,%s,%s,%s,%s,' % (
                        item0.b.contents[0],
                        item[i+1].contents[1].contents[0].strip(),
                        item[i+1].contents[3].contents[0].strip(),
                        item[i+1].contents[5].contents[0].strip(),
                        item[i+1].contents[7].contents[0].strip(),
                        'total' + unicode(i),
                    )
                    i += 1
            except:
                pass
            i += 1

        general = soup.findAll('table')[13].findAll('tr', 'subHeaderBack')[-1]
        grades += '%s,%s,%s,%s,%s,' % (
            general.b.contents[2][-2:].strip(),
            general.contents[1].span.contents[0].strip(),
            general.contents[1].b.contents[3].contents[0].strip(),
            general.contents[1].b.contents[5].contents[0].strip(),
            general.contents[1].b.contents[7].contents[0].strip(),
        )
        self.dionysos_grades = grades[:-1]

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
        except (AttributeError, IndexError):
            pass
        self.eclass_output = response.text

    def get_eclass_lessons(self, request = None):
        '''
        Get eclass lessons
        '''
        if not self.eclass_output:
            self.eclass_auth_login(request)
        try:
            eclass_output = BeautifulSoup(self.eclass_output).find('table', 'tbl_lesson').find_all('td', align='left')
            if request:
                from cronos.teilar.models import EclassLessons
                '''
                We are using the function from the webapp, all actions will be
                performed to the DB directly.
                Get all lessons and the ones that the student already follows
                '''
                eclass_lessons_all_q = EclassLessons.objects.all()
                eclass_lessons_following = eclass_lessons_all_q.filter(url__in = request.user.get_profile().following_eclass_lessons.all())
                '''
                Get the new list of following lessons
                '''
                new_eclass_lessons = []
                for eclass_lesson in eclass_output:
                    new_eclass_lessons.append(eclass_lesson.find('a')['href'])
                '''
                Convert the python list to QuerySet
                '''
                new_eclass_lessons = eclass_lessons_all_q.filter(url__in = new_eclass_lessons)
                '''
                Find the new additions and put them in the DB
                '''
                eclass_lessons_for_addition = new_eclass_lessons.exclude(url__in = eclass_lessons_following)
                for eclass_lesson in eclass_lessons_for_addition:
                    request.user.get_profile().following_eclass_lessons.add(eclass_lesson)
                '''
                Find the removed ones and remove them from the DB
                '''
                eclass_lessons_for_removal = eclass_lessons_following.exclude(url__in = new_eclass_lessons)
                for eclass_lesson in eclass_lessons_for_removal:
                    request.user.get_profile().following_eclass_lessons.remove(eclass_lesson)
            else:
                '''
                We are using the function from CLI, the output will be a python
                dictionary with the eclass lessons
                '''
                eclass_lessons = {}
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
