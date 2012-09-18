# -*- coding: utf-8 -*-

from cronos.common.exceptions import CronosError, LoginError
from cronos.common.log import log_extra_data
from cronos.teilar.models import EclassLessons
from cronos import dionysos_auth_login, eclass_auth_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_dionysos_last_name(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's last name from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        return unicode(output[5].find_all('td')[1].contents[0])
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Επωνύμου')

def get_dionysos_first_name(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's first name from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        return unicode(output[6].find_all('td')[1].contents[0])
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Ονόματος')

def get_dionysos_registration_number(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's registration number from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        return unicode(output[7].find_all('td')[1].contents[0])
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Αριθμού Μητρώου')

def get_dionysos_school(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's school from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        return unicode(output[8].find_all('td')[1].contents[0]).strip()
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Σχολής')

def get_dionysos_semester(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's semester from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        return unicode(output[9].findAll('td')[1].contents[0])
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Εξαμήνου')

def get_dionysos_introduction_year(output = None, request = None, username = None, password = None):
    '''
    Retrieves student's introduction year from dionysos.teilar.gr
    '''
    if not output:
        try:
            output = dionysos_auth_login(username, password, request, get_output = True)
        except (CronosError, LoginError):
            raise
    try:
        soup = BeautifulSoup(output).find_all('table')[15]
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
        return year + season
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Έτους Εισαγωγής')

def get_dionysos_declaration(username = None, password = None, request = None):
    '''
    Retrieves student's newest declaration from dionysos.teilar.gr
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

    Some of the above results are inside single HTML tags (<td>2</td>) and some
    are in double ones (<td><span>4</span</td>). We work around this with a
    try/except block.
    '''
    try:
        url = 'https://dionysos.teilar.gr/unistudent/stud_vClasses.asp?studPg=1&mnuid=diloseis;showDil&'
        output = dionysos_auth_login(username, password, request, url)
        soup = BeautifulSoup(output).find_all('table')[13].find_all('table')[0]

        '''
        Temp variables are named based on the HTML tags they contain. Those
        variables give faster results, since we don't have to regenerate the
        same data in each time the for loop is executed.
        '''
        temp_td_bottom = soup.find_all('td', 'bottomborderLight')
        declaration = temp_td_bottom
        i = 0
        while i < len(declaration):
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
        return ':'.join(declaration).replace('&amp;', '&')
    except (CronosError, LoginError):
        raise
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Δήλωσης')

def get_dionysos_grades(username = None, password = None):
    '''
    Retrieves student's grades from dionysos.teilar.gr
    '''
    try:
        '''
        The URL is different, so we need a new HTML output from dionysos
        '''
        url = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
        output = dionysos_auth_login(username, password, url, request)
        soup = BeautifulSoup(output)
        grades = u''
        i = 0
        '''
        Temp variables are named based on the HTML tags they contain. Those
        variables give faster results, since we don't have to regenerate the
        same data in each time the for loop is executed.
        '''
        temp_td = soup.findAll('table')[13].findAll('td')
        length_temp_td = len(temp_td)
        semesters = soup.findAll('table')[13].findAll('td', 'groupHeader')
        lessons = soup.findAll('table')[13].findAll('td', 'topBorderLight')
        while i < length_all_td:
            temp_td_item = temp_td[i]
            if temp_td_item in semesters:
                grades += str(item0.contents[0]) + ','
            '''elif temp_td_item in lessons:
                year = str(item[i+6].contents[0].i.contents[0]).strip()
                year = year[:10] + year[-9:]
                grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                    str(item0.contents[0]).strip(),
                    str(item[i+1].contents[0]).strip(),
                    str(item[i+2].contents[0]).strip(),
                    str(item[i+3].contents[0]).strip(),
                    str(item[i+4].contents[0]).strip(),
                    str(item[i+5].span.contents[0]).strip().replace(',', '.'),
                    year.replace('--', '-'),
                )
                try:
                    if item[i+9].contents[1].strip()[4] in [u'Θ', u'Ε']:
                        year = str(item[i+14].contents[0].i.contents[0]).strip()
                        year = year[:10] + year[-9:]
                        grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                            str(item[i+9].contents[1]).strip(),
                            '',
                            str(item[i+10].i.contents[0]).strip(),
                            str(item[i+11].contents[0]).strip(),
                            str(item[i+12].contents[0]).strip(),
                            str(item[i+13].contents[0]).strip().replace(',', '.'),
                            year.replace('--', '-'),
                        )
                        year = str(item[i+22].contents[0].i.contents[0])
                        year = year[:10] + year[-9:]
                        grades += '%s,%s,%s,%s,%s,%s,%s,' % (
                            str(item[i+17].contents[1]).strip(),
                            '',
                            str(item[i+18].i.contents[0]).strip(),
                            str(item[i+19].contents[0]).strip(),
                            str(item[i+20].contents[0]).strip(),
                            str(item[i+21].contents[0]).strip().replace(',', '.'),
                            year.replace('--', '-'),
                        )
                        i += 11
                except:
                    pass
                i += 6
            try:
                if item0.contents[0][:6] == u'Σύνολα':
                    grades += '%s,%s,%s,%s,%s,%s,' % (
                        str(item0.b.contents[0]),
                        str(item[i+1].contents[1].contents[0]).strip(),
                        str(item[i+1].contents[3].contents[0]).strip(),
                        str(item[i+1].contents[5].contents[0]).strip(),
                        str(item[i+1].contents[7].contents[0]).strip(),
                        'total' + str(i),
                    )
                    i += 1
            except:
                pass'''
            i += 1

        '''general = soup.findAll('table')[13].findAll('tr', 'subHeaderBack')[-1]
        grades += '%s,%s,%s,%s,%s,' % (
            str(general.b.contents[2][-2:]),
            str(general.contents[1].span.contents[0]),
            str(general.contents[1].b.contents[3].contents[0]),
            str(general.contents[1].b.contents[5].contents[0]),
            str(general.contents[1].b.contents[7].contents[0]),
        )
        return grades[:-1]'''
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Bαθμολογίας')

def get_eclass_lessons(request = None, username = None, password = None, output = None):
    '''
    Get eclass lessons
    '''
    if not output:
        try:
            output = eclass_auth_login(username, password, request)
        except (CronosError, LoginError):
            raise
    try:
        soup = BeautifulSoup(output).find('table', 'tbl_lesson').find_all('span', 'smaller')
        eclass_lessons = []
        for item in soup:
            '''
            Parse each lesson
            '''
            lesson = item.contents[0][1:-1]
            '''
            Get the lesson object from the DB
            '''
            lesson = EclassLessons.objects.get(url = u'http://openclass.teilar.gr/courses/%s/' % lesson)
            eclass_lessons.append(lesson)
        return eclass_lessons
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης μαθημάτων e-class')
