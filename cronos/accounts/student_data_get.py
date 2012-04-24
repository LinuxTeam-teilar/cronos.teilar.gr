# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.teilar.websites_login import dionysos_login
from cronos.log import CronosError, log_extra_data
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_dionysos_last_name(output = None, request = None, form = None):
    '''
    Retrieves student's last name from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[14].findAll('tr')[5].findAll('td')[1].contents[1]
        return unicode(soup)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Επωνύμου')

def get_dionysos_first_name(output = None, request = None, form = None):
    '''
    Retrieves student's first name from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[14].findAll('tr')[6].findAll('td')[1].contents[0]
        return unicode(soup)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Ονόματος')

def get_dionysos_registration_number(output = None, request = None, form = None):
    '''
    Retrieves student's registration number from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[14].findAll('tr')[7].findAll('td')[1].contents[0]
        return unicode(soup)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Αριθμού Μητρώου')

def get_dionysos_school(output = None, request = None, form = None):
    '''
    Retrieves student's school from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[14].findAll('tr')[8].findAll('td')[1].contents[0].strip()
        return unicode(soup)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Σχολής')

def get_dionysos_semester(output = None, request = None, form = None):
    '''
    Retrieves student's semester from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[14].findAll('tr')[9].findAll('td')[1].contents[0]
        return unicode(soup)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Εξαμήνου')

def get_dionysos_introduction_year(output = None, request = None, form = None):
    '''
    Retrieves student's introduction year from dionysos.teilar.gr
    '''
    try:
        soup = BeautifulSoup(output).findAll('table')[15]
        '''
        Introduction is in the following form:
        2004 - 2005 X or 2004 - 2005 E
        first_year - second_year season
        We need it in the form 2004X (YearSeason):
        if season is 'X', then year is first_year (2004X)
        if season is 'E', then year is second_year (2005E)
        '''
        season = unicode(soup.findAll('span','tablecell')[1].contents[0])[0]
        if season == u'Ε':
            year = unicode(soup.findAll('span','tablecell')[0].contents[0].split('-')[1])
        else:
            year = unicode(soup.findAll('span','tablecell')[0].contents[0].split('-')[0])
        return year + season
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Έτους Εισαγωγής')

def get_dionysos_declaration(username = None, password = None):
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
    Importance eg Y
    Grade (which in the latest declaration is always '-', so we skip it)

    Some of the above results are inside single HTML tags (<td>2</td>) and some
    are in double ones (<td><span ...>4</span</td>). We work around this with a
    try/except block.
    '''
    try:
        '''
        The link is different, so we need a new HTML output from dionysos
        '''
        link = 'https://dionysos.teilar.gr/unistudent/stud_vClasses.asp?studPg=1&mnuid=diloseis;showDil&'
        output = dionysos_login(username, password, link)
        soup = BeautifulSoup(output).findAll('table')[13].findAll('table')[0]
        '''
        Temp variables are named based on the HTML tags they contain. Those
        variables give faster results, since we don't have to regenerate the
        same data in each time the for loop is executed.
        '''
        temp_td_bottom = soup.findAll('td', 'bottomborderLight')
        declaration = temp_td_bottom
        while i < len(declaration):
            try:
                if unicode(declaration[i].contents[0].contents[0]) == u'-':
                    '''
                    Grade is always marked as - in the newest declaration, thus
                    we skip it.
                    '''
                    declaration.pop(i)
                else:
                    '''
                    Any other information that is inside double HTML tags is added.
                    '''
                    declaration[i] = unicode(declaration[i].contents[0].contents[0]).strip()
            except AttributeError:
                '''
                Add information that is inside single HTML tags
                '''
                declaration[i] = unicode(declaration[i].contents[0]).strip()
        return declaration.join(',').replace('&amp;', '&')
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης Δήλωσης')

def get_dionysos_grades(username = None, password = None):
    '''
    Retrieves student's grades from dionysos.teilar.gr
    '''
    try:
        '''
        The link is different, so we need a new HTML output from dionysos
        '''
        link = 'http://dionysos.teilar.gr/unistudent/stud_CResults.asp?studPg=1&mnuid=mnu3&'
        output = dionysos_login(username, password, link)
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

def get_eclass_lessons(output = None, request = None, form = None):
    try:
        soup = BeautifulSoup(output).find('table', 'FormData')
        eclass_lessons = ''
        i = 0
        for item in soup.findAll('a'):
            if (i % 2 == 0):
                eclass_lessons += '%s,' % (str(item.contents[0].split('-')[0]).strip())
            i += 1
        return eclass_lessons[:-1]
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(request, form))
        logger_mail.exception(error)
        raise CronosError(u'Αδυναμία ανάκτησης μαθημάτων e-class')
