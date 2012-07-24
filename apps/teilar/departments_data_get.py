# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
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
    departments_from_teilar = { department_id: 'name'}
    '''
    departments_from_teilar = {}
    output = teilar_login('teilar', 'departments')
    soup = BeautifulSoup(output)
    all_departments = soup.find_all('a', 'BlueText')
    for department in all_departments:
        department_id = int(department.get('href').split('=')[1])
        '''
        The string replace in the end is to keep it in track with dionysos.teilar.gr
        '''
        name = department.contents[0].replace(u'Τεχν.', u'Τεχνολογίας')
        departments_from_teilar[department_id] = name
    return departments_from_teilar

def add_department_to_db(department_id, name):
    department = Departments(
        urlid = department_id,
        name = name
    )
    try:
        department.save()
        status = u'Το %s προστέθηκε επιτυχώς' % (name)
        logger_syslog.info(status, extra = log_extra_data(cronjob = name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = name))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη του %s' % (name))
    return

def deprecate_department_in_db(department_id):
    '''
    Mark departments as deprecated
    '''
    department = Departments.objects.get(urlid = department_id)
    department.deprecated = True
    try:
        department.save()
        status = u'Το %s άλλαξε κατάσταση σε deprecated' % (department.name)
        logger_syslog.info(status, extra = log_extra_data(cronjob = department.name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = department.name))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την αλλαγή κατάστασης του %s σε deprecated' % (department.name))
    return

def update_departments():
    '''
    1) Find departments that are no longer valid and remove them
    2) Find new departments and add them
    '''
    departments_from_teilar = get_departments()
    '''
    Get all the departments from the DB and put them in a dictionary in the structure:
    departments_from_db = { department_id: 'name' }
    '''
    departments_from_db = {}
    departments_from_db_q = Departments.objects.filter(deprecated = False)
    for department in departments_from_db_q:
        departments_from_db[department.urlid] = department.name
    '''
    Get the department_IDs in set data structure format, for easier comparisons
    '''
    departments_from_teilar_ids = set(departments_from_teilar.keys())
    try:
        departments_from_db_ids = set(departments_from_db.keys())
    except AttributeError:
        '''
        Departments table is empty in the DB
        '''
        departments_from_db_ids = set()
    '''
    Get ex departments and mark them as deprecated
    '''
    ex_departments = departments_from_db_ids - departments_from_teilar_ids
    for department_id in ex_departments:
        deprecate_department_in_db(department_id)
    '''
    Get new departments and add them to the DB
    '''
    new_departments = departments_from_teilar_ids - departments_from_db_ids
    for department_id in new_departments:
        add_department_to_db(department_id, departments_from_teilar[department_id])
    return

if __name__ == '__main__':
    try:
        update_departments()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
