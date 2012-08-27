# -*- coding: utf-8 -*-

from cronos import CronosError, log_extra_data
from cronos.accounts.encryption import decrypt_password
from cronos.accounts.student_data_get import *
from cronos.accounts.student_data_to_db import add_student_to_db
from bs4 import BeautifulSoup
from django.contrib.auth.models import User

class DionysosTeilarAuthentication(object):
    '''
    Custom authentication backend. It uses dionysos.teilar.gr to
    authenticate the student.
    '''
    def authenticate(self, username = None, password = None, request = None):
        '''
        Try to authenticate the user. If there isn't such user
        in the Django DB, try to find the user in dionysos.teilar.gr
        '''
        return self.get_or_create_user(username, password, request)

    def get_user(self, user_id):
        '''
        Retrieve a specific user from the Django DB
        '''
        try:
            return User.objects.get(pk = user_id)
        except User.DoesNotExist:
            return

    def get_or_create_user(self, username = None, password = None, request = None):
        '''
        Retrieves the user from the Django DB. If the user is not
        found in the DB, then it tries to retrieve him from
        dionysos.teilar.gr
        '''
        try:
            '''
            Try to pull the user from the Django DB
            '''
            user = User.objects.get(username = username)
            '''
            If the user is found in the DB, try to login with those
            credentials in dionysos.teilar.gr
            '''
            try:
                if not dionysos_login(username, password):
                    return
            except CronosError:
                '''
                Connection issue with dionysos.teilar.gr. Try to authenticate
                with the password stored in the DB instead
                '''
                if password != decrypt_password(user.get_profile().dionysos_password):
                    return
        except User.DoesNotExist:
            '''
            If the user is not in the DB, try to log in with his
            dionysos.teilar.gr account
            '''
            try:
                output = dionysos_login(username, password, request = request)
            except CronosError:
                raise
            if output:
                '''
                The credentials worked, try to create a user based on those credentials
                '''
                credentials = {
                        'username': username,
                        'password': password,
                }
                try:
                    front_page = BeautifulSoup(output).find_all('table')[14].find_all('tr')
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(username, request))
                    logger_mail.exception(error)
                    raise CronosError(u'Αδυναμία ανάκτησης στοιχείων χρήστη')
                try:
                    credentials['last_name'] = get_dionysos_last_name(front_page, username, request)
                    credentials['first_name'] = get_dionysos_first_name(front_page, username, request)
                    credentials['registration_number'] = get_dionysos_registration_number(front_page, username, request)
                    credentials['semester'] = get_dionysos_semester(front_page, username, request)
                    credentials['school'] = get_dionysos_school(front_page, username, request)
                    credentials['introduction_year'] = get_dionysos_introduction_year(output, username, request)
                    credentials['declaration'] = get_dionysos_declaration(username, password, request)
                    #credentials['grades'] = get_dionysos_grades(username, password, request)
                    user = add_student_to_db(credentials, request)
                except CronosError:
                    raise
            else:
                return
        return user
