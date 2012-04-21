# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from bs4 import BeautifulSoup
from cronos.log import CronosError, log_extra_data
from cronos.teilar.models import Departments
import logging
import StringIO
import pycurl

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_departments():
    '''
    Retrieves the departments from teilar.gr
    The output is dictionary with the following structure:
    departments_from_teilar = { department_id: 'name'}
    '''
    departments_from_teilar = {}
    conn = pycurl.Curl()
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'http://www.teilar.gr/schools.php')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = unicode(b.getvalue(), 'utf-8', 'ignore')
    soup = BeautifulSoup(output)
    all_departments = soup.find_all('a', 'BlueText')
    for department in all_departments:
        department_id = department.get('href').split('=')[1]
        name = department.contents[0].replace(u'Τεχν.', u'Τεχνολογίας')
        departments_from_teilar[int(department_id)] = name
    return departments_from_teilar

def add_department_to_db(department_id, name):
    department = Departments(
        urlid = department_id,
        name = name
    )
    try:
        department.save()
        status = u'Το %s με ID %s προστέθηκε στη βάση δεδομένων επιτυχώς' % (name, department_id)
        logger_syslog.info(status, extra = log_extra_data())
        logger_mail.info(status)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.error(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη του %s με ID %s' % (name, department_id))
    return

def remove_department_from_db(department_id):
    print 'Removed %s from DB' % (department_id)
    return

def update_departments():
    '''
    1) Find departments that are no longer valid and remove them
    2) Find new departments and add them
    '''
    departments_from_teilar = get_departments()
    '''
    Get all the departments from the DB and put them in a dictionary in the structure:
    departments_from_db = {department_id: 'name'}
    '''
    departments_from_db = {}
    departments_from_db_q = Departments.objects.all()
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
    Get ex departments and remove them from the DB
    '''
    # Need to find out what will happen with relations first
    #ex_departments = departments_from_db_ids - departments_from_teilar_ids
    #for department_id in ex_departments:
    #    remove_department_from_db(department_id)
    '''
    Get new departments and remove them from the DB
    '''
    new_departments = departments_from_teilar_ids - departments_from_db_ids
    for department_id in new_departments:
        add_department_to_db(department_id, departments_from_teilar[department_id])
    return

if __name__ == '__main__':
    try:
        update_departments()
    except CronosError as error:
        logger_syslog.error(error, extra = log_extra_data)
