# -*- coding: utf-8 -*-

from cronos.common.exceptions import CronosError
from cronos.common.log import log_extra_data
from cronos.posts.models import Authors
from cronos.teilar.models import Departments
from cronos import teilar_anon_login
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')


class Command(BaseCommand):
    def get_departments(self):
        '''
        Retrieves the departments from teilar.gr
        The output is dictionary with the following structure:
        departments_from_teilar = {'url': 'name'}
        '''
        departments_from_teilar = {}
        output = teilar_anon_login('http://www.teilar.gr/schools.php')
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

    def add_department_to_db(self, url, name):
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

    def deprecate_department_in_db(self, url, departments_from_db_q):
        '''
        Mark departments as inactive
        '''
        department = departments_from_db_q.get(url = url)
        department.is_active = False
        try:
            department.save()
            logger_syslog.info(u'Αλλαγή κατάστασης σε inactive', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
        return

    def update_departments(self):
        '''
        1) Find departments that are no longer valid and remove them
        2) Find new departments and add them
        '''
        departments_from_teilar = self.get_departments()
        '''
        Get all the departments from the DB and put them in a dictionary in the structure:
        departments_from_db = {'url': 'name'}
        '''
        departments_from_db = {}
        try:
            departments_from_db_q = Departments.objects.filter(is_active = True)
            for department in departments_from_db_q:
                departments_from_db[department.url] = department.name
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')

        '''
        Get the URLs in set data structure format, for easier comparisons
        '''
        departments_from_teilar_set = set(departments_from_teilar.keys())
        try:
            departments_from_db_set = set(departments_from_db.keys())
        except AttributeError:
            '''
            Departments table is empty in the DB
            '''
            departments_from_db_set = set()
        '''
        Get ex departments and mark them as inactive
        '''
        ex_departments = departments_from_db_set - departments_from_teilar_set
        for url in ex_departments:
            self.deprecate_department_in_db(url, departments_from_db_q)
        '''
        Get new departments and add them to the DB
        '''
        new_departments = departments_from_teilar_set - departments_from_db_set
        for url in new_departments:
            self.add_department_to_db(url, departments_from_teilar[url])
        return

    def handle(self, *args, **options):
        self.update_departments()
