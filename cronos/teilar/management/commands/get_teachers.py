# -*- coding: utf-8 -*-

from cronos.common.log import CronosError, log_extra_data
from cronos.announcements.models import Authors
from cronos.teilar.models import Departments, Teachers
from cronos.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

class Command(BaseCommand):
    def get_teachers(self):
        '''
        Retrieves the teachers from teilar.gr
        The output is dictionary with the following structure:
        teachers_from_teilar = {'url': ['name', 'email', 'department']}
        '''
        teachers_from_teilar = {}
        for pid in range(400):
            if pid == 386:
                '''
                Dirty workaround to avoid a teacher who has no matching department,
                probably because they are testing something
                '''
                continue
            '''
            Perform connections to each of the teacher's profile page. From the HTML
            output we grab the name, email and department
            '''
            url = 'http://www.teilar.gr/person.php?pid=%s' % pid
            output = teilar_login(url)
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
            teachers_from_teilar[url] = [name, email, department]
        return teachers_from_teilar

    def add_teacher_to_db(self, url, attributes, departments_from_db_q):
        name = attributes[0]
        email = attributes[1]
        try:
            department = departments_from_db_q.get(name = attributes[2])
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
            return
        teacher = Teachers(
            url = url,
            name = name,
            email = email,
            department = department,
        )
        try:
            teacher.save()
            logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
            return
        author = Authors(content_object = teacher)
        try:
            author.save()
            logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
        return

    def deprecate_teacher_in_db(self, url, teachers_from_db_q):
        '''
        Mark teachers as deprecated
        '''
        teacher = teachers_from_db_q.get(url = url)
        teacher.deprecated = True
        try:
            teacher.save()
            logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
        return

    def update_teachers(self):
        '''
        1) Find teachers that left the school mark them as deprecated
        2) Find new teachers and add them
        3) In the existing teachers, find changes in their attributes and
        update them accordingly
        '''
        teachers_from_teilar = self.get_teachers()
        '''
        Get all the teachers from the DB and put them in a dictionary in the structure:
        teachers_from_db = {'url': ['name', 'email', 'department']}
        '''
        teachers_from_db = {}
        try:
            teachers_from_db_q = Teachers.objects.filter(deprecated = False)
            departments_from_db_q = Departments.objects.filter(deprecated = False)
            for teacher in teachers_from_db_q:
                teachers_from_db[teacher.url] = [teacher.name, teacher.email, teacher.department]
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
        '''
        Get the teacher_URLs in set data structure, for easier comparisons
        '''
        teachers_from_teilar_set = set(teachers_from_teilar.keys())
        try:
            teachers_from_db_set = set(teachers_from_db.keys())
        except AttributeError:
            '''
            Teachers table is empty in the DB
            '''
            teachers_from_db_set = set()
        '''
        Get ex teachers and mark them as deprecated
        '''
        ex_teachers = teachers_from_db_set - teachers_from_teilar_set
        for url in ex_teachers:
            self.deprecate_teacher_in_db(url, teachers_from_db_q)
        '''
        Get new teachers and add them to the DB
        '''
        new_teachers = teachers_from_teilar_set - teachers_from_db_set
        for url in new_teachers:
            self.add_teacher_to_db(url, teachers_from_teilar[url], departments_from_db_q)
        '''
        Get all the existing teachers, and check if any of their attributes were updated
        '''
        existing_teachers = teachers_from_teilar_set & teachers_from_db_set
        for url in existing_teachers:
            i = 0
            teacher = teachers_from_db_q.get(url = url)
            for attribute in teachers_from_teilar[url]:
                if teachers_from_db[url][i] != attribute:
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
                        teacher.department = departments_from_db_q.get(name = attribute)
                    try:
                        teacher.save()
                        status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                        logger_syslog.info(status, extra = log_extra_data(url))
                    except Exception as error:
                        logger_syslog.error(error, extra = log_extra_data(url))
                        logger_mail.exception(error)
                i += 1
        return

    def handle(self, *args, **options):
        self.update_teachers()
