# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Authors
from apps.teilar.models import Departments
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_departments():
    '''
    Retrieves the departments from teilar.gr
    The output is dictionary with the following structure:
    departments_from_teilar = {'url': 'name'}
    '''
    departments_from_teilar = {}
    output = teilar_login('http://www.teilar.gr/schools.php')
    soup = BeautifulSoup(output)
    all_departments = soup.find_all('a', 'BlueText')
    for department in all_departments:
        url = 'http://www.teilar.gr/' + department.get('href')
        '''
        The string replace in the end is to keep it in track with dionysos.teilar.gr
        '''
        name = department.contents[0].replace(u'Τεχν.', u'Τεχνολογίας')
        departments_from_teilar[url] = name
    return departments_from_teilar

def add_department_to_db(url, name):
    department = Departments(
        url = url,
        name = name,
    )
    try:
        department.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
        return
    author = Authors(content_object = department)
    try:
        author.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def deprecate_department_in_db(url, departments_from_db_q):
    '''
    Mark departments as deprecated
    '''
    department = departments_from_db_q.get(url = url)
    department.deprecated = True
    try:
        department.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def update_departments():
    '''
    1) Find departments that are no longer valid and remove them
    2) Find new departments and add them
    '''
    departments_from_teilar = get_departments()
    '''
    Get all the departments from the DB and put them in a dictionary in the structure:
    departments_from_db = {'url': 'name'}
    '''
    departments_from_db = {}
    try:
        departments_from_db_q = Departments.objects.filter(deprecated = False)
        for department in departments_from_db_q:
            departments_from_db[department.url] = department.name
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')

    '''
    Get the URLs in set data structure format, for easier comparisons
    '''
    departments_from_teilar_urls = set(departments_from_teilar.keys())
    try:
        departments_from_db_urls = set(departments_from_db.keys())
    except AttributeError:
        '''
        Departments table is empty in the DB
        '''
        departments_from_db_urls = set()
    '''
    Get ex departments and mark them as deprecated
    '''
    ex_departments = departments_from_db_urls - departments_from_teilar_urls
    for url in ex_departments:
        deprecate_department_in_db(url, departments_from_db_q)
    '''
    Get new departments and add them to the DB
    '''
    new_departments = departments_from_teilar_urls - departments_from_db_urls
    for url in new_departments:
        add_department_to_db(url, departments_from_teilar[url])
    return

if __name__ == '__main__':
    try:
        update_departments()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
