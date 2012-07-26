# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.eclass.models import Faculties, Lessons
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_lessons():
    '''
    Retrieves the lessons from eclass.teilar.gr
    The output is dictionary with the following structure:
    lessons_from_eclass = { 'lesson_id': ['name', 'teacher', 'faculty', 'ltype'] }
    '''
    lessons_from_eclass = {}
    faculties = Faculties.objects.all()
    for faculty in faculties:
        output = teilar_login('eclass', 'lessons', faculty.urlid)
        soup = BeautifulSoup(output)
        for i in range(2):
            '''
            Lessons are grouped in three types:
            Undergraduate, Graduate, Other
            '''
            ltype = BeautifulSoup(str(soup.find_all('table', id='t%s' % i)))
            if not ltype:
                '''
                If the lesson type does not exist, then move on
                '''
                continue
            all_lessons = ltype.find_all('tr', 'even') + ltype.find_all('tr', 'odd')
            for lesson in all_lessons:
                lesson_id = lesson.small.contents[0].replace('(', '').replace(')', '')
                try:
                    name = lesson.a.contents[0]
                except AttributeError:
                    name = lesson.find_all('td')[1].contents[0].strip()
                try:
                    teacher = lesson.find_all('td')[2].contents[0].strip()
                except IndexError:
                    teacher = None
                if i == 0:
                    ltype = u'Προπτυχιακό'
                elif i == 1:
                    ltype = u'Μεταπτυχιακό'
                elif i == 2:
                    ltype == u'Άλλο'
                lessons_from_eclass[lesson_id] = [unicode(name), unicode(teacher), faculty.name, ltype]
    return lessons_from_eclass

def add_lesson_to_db(lesson_id, attributes):
    name = attributes[0]
    teacher = attributes[1]
    faculty = Faculties.objects.get(name = attributes[2])
    ltype = attributes[3]
    lesson = Lessons(
        urlid = lesson_id,
        name = name,
        teacher = teacher,
        faculty = faculty,
        ltype = ltype,
    )
    try:
        lesson.save()
        status = u'Το %s προστέθηκε επιτυχώς' % name
        logger_syslog.info(status, extra = log_extra_data(cronjob = name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = name))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη του %s' % name)
    return

def deprecate_lesson_in_db(lesson_id):
    '''
    Mark lessons as deprecated
    '''
    lesson = Lessons.objects.get(urlid = lesson_id)
    lesson.deprecated = True
    try:
        lesson.save()
        status = u'Το %s άλλαξε κατάσταση σε deprecated' % (lesson.name)
        logger_syslog.info(status, extra = log_extra_data(cronjob = lesson.name))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = lesson.name))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την αλλαγή κατάστασης του %s σε deprecated' % (lesson.name))
    return

def update_lessons():
    '''
    1) Find lessons that are no longer valid and remove them
    2) Find new lessons and add them
    '''
    lessons_from_eclass = get_lessons()
    '''
    Get all the lessons from the DB and put them in a dictionary in the structure:
    lessons_from_db = { 'lesson_id': ['name', 'teacher', 'faculty', 'ltype'] }
    '''
    lessons_from_db = {}
    lessons_from_db_q = Lessons.objects.filter(deprecated = False)
    for lesson in lessons_from_db_q:
        lessons_from_db[lesson.urlid] = [lesson.name, lesson.teacher, lesson.faculty, lesson.ltype]
    '''
    Get the lesson_IDs in set data structure format, for easier comparisons
    '''
    lessons_from_eclass_ids = set(lessons_from_eclass.keys())
    try:
        lessons_from_db_ids = set(lessons_from_db.keys())
    except AttributeError:
        '''
        Lessons table is empty in the DB
        '''
        lessons_from_db_ids = set()
    '''
    Get ex lessons and mark them as deprecated
    '''
    ex_lessons = lessons_from_db_ids - lessons_from_eclass_ids
    for lesson_id in ex_lessons:
        deprecate_lesson_in_db(lesson_id)
    '''
    Get new lessons and add them to the DB
    '''
    new_lessons = lessons_from_eclass_ids - lessons_from_db_ids
    for lesson_id in new_lessons:
        add_lesson_to_db(lesson_id, lessons_from_eclass[lesson_id])
    '''
    Get all the existing lessons, and check if any of their attributes were updated
    '''
    existing_lessons = lessons_from_eclass_ids & lessons_from_db_ids
    for lesson_id in existing_lessons:
        i = 0
        lesson = Lessons.objects.get(urlid = lesson_id)
        for attribute in lessons_from_eclass[lesson_id]:
            if lessons_from_db[lesson_id][i] != attribute:
                if i == 0:
                    attr_name = u'name'
                    lesson.name = attribute
                elif i == 1:
                    attr_name = u'teacher'
                    lesson.teacher = attribute
                elif i == 2:
                    '''
                    The faculty is stored as a foreign key of the
                    Faculties table, thus it needs an extra check
                    '''
                    if attribute.strip() == unicode(lesson.faculty).strip():
                        i += 1
                        continue
                    attr_name = u'faculty'
                    lesson.faculty = Faculties.objects.get(name = attribute)
                elif i == 3:
                    attr_name = u'ltype'
                    lesson.ltype = attribute
                try:
                    lesson.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(cronjob = lesson.name))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(cronjob = lesson.name))
                    logger_mail.exception(error)
                    raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την αλλαγή κατάστασης του %s σε %s' % (attr_name, attribute))
            i += 1
    return

if __name__ == '__main__':
    try:
        update_lessons()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
