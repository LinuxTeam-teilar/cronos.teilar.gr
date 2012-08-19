# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Authors
from apps.eclass.models import Faculties, Lessons
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_lessons(faculties_from_db_q):
    '''
    Retrieves the lessons from eclass.teilar.gr
    The output is dictionary with the following structure:
    lessons_from_eclass = {'url': ['name', 'teacher', 'faculty', 'ltype'] }
    '''
    lessons_from_eclass = {}
    for faculty in faculties_from_db_q:
        output = teilar_login(faculty.url)
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
                url = lesson.small.contents[0].replace('(', '').replace(')', '')
                url = u'http://openclass.teilar.gr/courses/%s/' % url
                try:
                    name = lesson.a.contents[0].strip()
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
                lessons_from_eclass[url] = [unicode(name), unicode(teacher), faculty.name, ltype]
    return lessons_from_eclass

def add_lesson_to_db(url, attributes, faculties_from_db_q):
    name = attributes[0]
    teacher = attributes[1]
    faculty = faculties_from_db_q.get(name = attributes[2])
    ltype = attributes[3]
    lesson = Lessons(
        url = url,
        name = name,
        teacher = teacher,
        faculty = faculty,
        ltype = ltype,
    )
    try:
        lesson.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
        return
    author = Authors(content_object = lesson)
    try:
        author.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def deprecate_lesson_in_db(url, lessons_from_db_q):
    '''
    Mark lessons as deprecated
    '''
    lesson = lessons_from_db_q.get(url = url)
    lesson.deprecated = True
    try:
        lesson.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(url))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(url))
        logger_mail.exception(error)
    return

def update_lessons():
    '''
    1) Find lessons that are no longer valid and remove them
    2) Find new lessons and add them
    '''
    try:
        faculties_from_db_q = Faculties.objects.filter(deprecated = False)
        lessons_from_eclass = get_lessons(faculties_from_db_q)
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
    '''
    Get all the lessons from the DB and put them in a dictionary in the structure:
    lessons_from_db = {'url': ['name', 'teacher', 'faculty', 'ltype']}
    '''
    lessons_from_db = {}
    lessons_from_db_q = Lessons.objects.filter(deprecated = False)
    for lesson in lessons_from_db_q:
        lessons_from_db[lesson.url] = [lesson.name, lesson.teacher, lesson.faculty, lesson.ltype]
    '''
    Get the lesson_IDs in set data structure format, for easier comparisons
    '''
    lessons_from_eclass_urls = set(lessons_from_eclass.keys())
    try:
        lessons_from_db_urls = set(lessons_from_db.keys())
    except AttributeError:
        '''
        Lessons table is empty in the DB
        '''
        lessons_from_db_urls = set()
    '''
    Get ex lessons and mark them as deprecated
    '''
    ex_lessons = lessons_from_db_urls - lessons_from_eclass_urls
    for url in ex_lessons:
        deprecate_lesson_in_db(url, lessons_from_db_q)
    '''
    Get new lessons and add them to the DB
    '''
    new_lessons = lessons_from_eclass_urls - lessons_from_db_urls
    for url in new_lessons:
        add_lesson_to_db(url, lessons_from_eclass[url], faculties_from_db_q)
    '''
    Get all the existing lessons, and check if any of their attributes were updated
    '''
    existing_lessons = lessons_from_eclass_urls & lessons_from_db_urls
    for url in existing_lessons:
        i = 0
        lesson = lessons_from_db_q
        for attribute in lessons_from_eclass[url]:
            if lessons_from_db[url][i] != attribute:
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
                    lesson.faculty = faculties_from_db_q
                elif i == 3:
                    attr_name = u'ltype'
                    lesson.ltype = attribute
                try:
                    lesson.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(url))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(url))
                    logger_mail.exception(error)
            i += 1
    return

if __name__ == '__main__':
    try:
        update_lessons()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
