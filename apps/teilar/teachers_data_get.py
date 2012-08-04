# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.teilar.models import Departments, Teachers
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_teachers():
    '''
    Retrieves the teachers from teilar.gr
    The output is dictionary with the following structure:
    teachers_from_teilar = { teacher_id: ['name', 'email', 'department'] }
    '''
    teachers_from_teilar = {}
    for pid in range(400):
        '''
        Perform connections to each of the teacher's profile page. From the HTML
        output we grab the name, email and department
        '''
        output = teilar_login('teilar', 'teachers', pid)
        soup = BeautifulSoup(output)
        name = None
        email = None
        department = None
        try:
            name = soup.findAll('td', 'BlackText11Bold')[1].contents[0].strip()
        except IndexError:
            '''
            No teacher found, continue with the next item of the loop
            '''
            continue
        try:
            email = soup.findAll('td', 'BlackText11')[5].a.contents[0].split(' ')[0].strip()
        except AttributeError:
            try:
                email = soup.findAll('td', 'BlackText11')[5].contents[0].strip()
            except IndexError:
                pass
        except IndexError:
            pass
        try:
            '''
            The string replace in the end is to keep it in track with dionysos.teilar.gr
            '''
            department = soup.findAll('td', 'BlackText11')[2].contents[0].strip().replace(u'Τεχν.', u'Τεχνολογίας')
        except IndexError:
            pass
        teachers_from_teilar[pid] = [name, email, department]
    return teachers_from_teilar

def add_teacher_to_db(teacher_id, attributes):
    try:
        name = attributes[0]
        email = attributes[1]
        department = Departments.objects.get(name = attributes[2])
        teachers = Teachers(
            urlid = teacher_id,
            name = name,
            email = email,
            department = department,
        )
        teachers.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(name))
        logger_mail.exception(error)
    return

def deprecate_teacher_in_db(teacher_id):
    '''
    Mark teachers as deprecated
    '''
    teacher = Teachers.objects.get(urlid = teacher_id)
    teacher.deprecated = True
    try:
        teacher.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(teacher.name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(teacher.name))
        logger_mail.exception(error)
    return

def update_teachers():
    '''
    1) Find teachers that left the school mark them as deprecated
    2) Find new teachers and add them
    3) In the existing teachers, find changes in their attributes and
    update them accordingly
    '''
    teachers_from_teilar = get_teachers()
    '''
    Get all the teachers from the DB and put them in a dictionary in the structure:
    teachers_from_db = { teacher_id: ['name', 'email', 'department'] }
    '''
    teachers_from_db = {}
    try:
        teachers_from_db_q = Teachers.objects.filter(deprecated = False)
        for teacher in teachers_from_db_q:
            teachers_from_db[teacher.urlid] = [teacher.name, teacher.email, teacher.department]
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')

    '''
    Get the teacher_IDs in set data structure, for easier comparisons
    '''
    teachers_from_teilar_ids = set(teachers_from_teilar.keys())
    try:
        teachers_from_db_ids = set(teachers_from_db.keys())
    except AttributeError:
        '''
        Teachers table is empty in the DB
        '''
        teachers_from_db_ids = set()
    '''
    Get ex teachers and mark them as deprecated
    '''
    ex_teachers = teachers_from_db_ids - teachers_from_teilar_ids
    for teacher_id in ex_teachers:
        deprecate_teacher_in_db(teacher_id)
    '''
    Get new teachers and add them to the DB
    '''
    new_teachers = teachers_from_teilar_ids - teachers_from_db_ids
    for teacher_id in new_teachers:
        add_teacher_to_db(teacher_id, teachers_from_teilar[teacher_id])
    '''
    Get all the existing teachers, and check if any of their attributes were updated
    '''
    existing_teachers = teachers_from_teilar_ids & teachers_from_db_ids
    for teacher_id in existing_teachers:
        i = 0
        teacher = Teachers.objects.get(urlid = teacher_id)
        for attribute in teachers_from_teilar[teacher_id]:
            if teachers_from_db[teacher_id][i] != attribute:
                if i == 0:
                    attr_name = u'name'
                    teacher.name = attribute
                elif i == 1:
                    attr_name = u'email'
                    teacher.email = attribute
                elif i == 2:
                    '''
                    The department is saved as a foreign key of the
                    Departments table, thus it needs an extra check
                    '''
                    if attribute.strip() == unicode(teacher.department).strip():
                        continue
                    attr_name = u'department'
                    teacher.department = Departments.objects.get(name = attribute)
                try:
                    teacher.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(teacher.name))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(teacher.name))
                    logger_mail.exception(error)
            i += 1
    return

if __name__ == '__main__':
    try:
        update_teachers()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
