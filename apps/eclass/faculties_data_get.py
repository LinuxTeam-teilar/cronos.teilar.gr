# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
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
    faculties_from_eclass = { faculty_id: ['name', 'code'] }
    '''
    faculties_from_eclass = {}
    output = teilar_login('eclass', 'faculties')
    soup = BeautifulSoup(output)
    all_faculties = soup.table('td')
    for faculty in all_faculties:
        faculty_id = int(faculty.a.get('href').split('=')[1])
        name = faculty.a.contents[0].strip()
        code = faculty.small.contents[0].split(')')[0].replace('(', '').strip()
        faculties_from_eclass[faculty_id] = [name, code]
    return faculties_from_eclass

def add_faculty_to_db(faculty_id, attributes):
    name = attributes[0]
    code = attributes[1]
    faculty = Faculties(
        urlid = faculty_id,
        name = name,
        code = code,
    )
    try:
        faculty.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(cronjob = name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = name))
        logger_mail.exception(error)
    return

def deprecate_faculty_in_db(faculty_id):
    '''
    Mark faculties as deprecated
    '''
    faculty = Faculties.objects.get(urlid = faculty_id)
    faculty.deprecated = True
    try:
        faculty.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(cronjob = faculty.name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = faculty.name))
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
    faculties_from_db = { faculty_id: ['name', 'code'] }
    '''
    faculties_from_db = {}
    faculties_from_db_q = Faculties.objects.filter(deprecated = False)
    for faculty in faculties_from_db_q:
        faculties_from_db[faculty.urlid] = [faculty.name, faculty.code]
    '''
    Get the faculty_IDs in set data structure format, for easier comparisons
    '''
    faculties_from_eclass_ids = set(faculties_from_eclass.keys())
    try:
        faculties_from_db_ids = set(faculties_from_db.keys())
    except AttributeError:
        '''
        Faculties table is empty in the DB
        '''
        faculties_from_db_ids = set()
    '''
    Get ex faculties and mark them as deprecated
    '''
    ex_faculties = faculties_from_db_ids - faculties_from_eclass_ids
    for faculty_id in ex_faculties:
        deprecate_faculty_in_db(faculty_id)
    '''
    Get new faculties and add them to the DB
    '''
    new_faculties = faculties_from_eclass_ids - faculties_from_db_ids
    for faculty_id in new_faculties:
        add_faculty_to_db(faculty_id, faculties_from_eclass[faculty_id])
    '''
    Get all the existing faculties, and check if any of their attributes were updated
    '''
    existing_faculties = faculties_from_eclass_ids & faculties_from_db_ids
    for faculty_id in existing_faculties:
        i = 0
        faculty = Faculties.objects.get(urlid = faculty_id)
        for attribute in faculties_from_eclass[faculty_id]:
            if faculties_from_db[faculty_id][i] != attribute:
                if i == 0:
                    attr_name = u'name'
                    faculty.name = attribute
                elif i == 1:
                    attr_name = u'code'
                    faculty.code = attribute
                try:
                    faculty.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(cronjob = faculty.name))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(cronjob = faculty.name))
                    logger_mail.exception(error)
            i += 1
    return

if __name__ == '__main__':
    try:
        update_faculties()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
