# -*- coding: utf-8 -*-

import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__)) + '/../..'
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Authors
from apps.eclass.models import Faculties
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_faculties():
    '''
    Retrieves the faculties from eclass.teilar.gr
    The output is dictionary with the following structure:
    faculties_from_eclass = {'url': ['name', 'code']}
    '''
    faculties_from_eclass = {}
    output = teilar_login('http://openclass.teilar.gr/modules/auth/listfaculte.php')
    soup = BeautifulSoup(output)
    all_faculties = soup.table('td')
    for faculty in all_faculties:
        url = 'http://openclass.teilar.gr/modules/auth/' + faculty.a.get('href')
        name = faculty.a.contents[0].strip()
        code = faculty.small.contents[0].split(')')[0].replace('(', '').strip()
        faculties_from_eclass[url] = [name, code]
    return faculties_from_eclass

def add_faculty_to_db(url, attributes):
    name = attributes[0]
    code = attributes[1]
    faculty = Faculties(
        url = url,
        name = name,
        code = code,
    )
    try:
        faculty.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
        return
    author = Authors(content_object = faculty)
    try:
        author.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def deprecate_faculty_in_db(url, faculties_from_db_q):
    '''
    Mark faculties as deprecated
    '''
    faculty = faculties_from_db_q.get(url = url)
    faculty.deprecated = True
    try:
        faculty.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def update_faculties():
    '''
    1) Find faculties that are no longer valid and remove them
    2) Find new faculties and add them
    '''
    faculties_from_eclass = get_faculties()
    '''
    Get all the faculties from the DB and put them in a dictionary in the structure:
    faculties_from_db = {'url': ['name', 'code']}
    '''
    try:
        faculties_from_db = {}
        faculties_from_db_q = Faculties.objects.filter(deprecated = False)
        for faculty in faculties_from_db_q:
            faculties_from_db[faculty.url] = [faculty.name, faculty.code]
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
    '''
    Get the faculty_IDs in set data structure format, for easier comparisons
    '''
    faculties_from_eclass_set = set(faculties_from_eclass.keys())
    try:
        faculties_from_db_set = set(faculties_from_db.keys())
    except AttributeError:
        '''
        Faculties table is empty in the DB
        '''
        faculties_from_db_set = set()
    '''
    Get ex faculties and mark them as deprecated
    '''
    ex_faculties = faculties_from_db_set - faculties_from_eclass_set
    for url in ex_faculties:
        deprecate_faculty_in_db(url, faculties_from_db_q)
    '''
    Get new faculties and add them to the DB
    '''
    new_faculties = faculties_from_eclass_set - faculties_from_db_set
    for url in new_faculties:
        add_faculty_to_db(url, faculties_from_eclass[url])
    '''
    Get all the existing faculties, and check if any of their attributes were updated
    '''
    existing_faculties = faculties_from_eclass_set & faculties_from_db_set
    for url in existing_faculties:
        i = 0
        faculty = faculties_from_db_q.get(url = url)
        for attribute in faculties_from_eclass[url]:
            if faculties_from_db[url][i] != attribute:
                if i == 0:
                    attr_name = u'name'
                    faculty.name = attribute
                elif i == 1:
                    attr_name = u'code'
                    faculty.code = attribute
                try:
                    faculty.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(url))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(url))
                    logger_mail.exception(error)
            i += 1
    return

if __name__ == '__main__':
    try:
        update_faculties()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
