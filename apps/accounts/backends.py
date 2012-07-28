# -*- coding: utf-8 -*-

from apps import CronosError
from apps.accounts.encryption import decrypt_password
from apps.accounts.student_data_get import *
from apps.accounts.student_data_to_db import add_student_to_db
from django.contrib.auth.models import User

class DionysosTeilarAuthentication(object):
    '''
    Custom authentication backend. It uses dionysos.teilar.gr to
    authenticate the student.
    '''
    def authenticate(self, username = None, password = None, request = None, form = None):
        '''
        Try to authenticate the user. If there isn't such user
        in the Django DB, try to find the user in dionysos.teilar.gr
        '''
        return self.get_or_create_user(username, password, request, form)

    def get_user(self, user_id):
        '''
        Retrieve a specific user from the Django DB
        '''
        try:
            return User.objects.get(pk = user_id)
        except User.DoesNotExist:
            return

    def get_or_create_user(self, username = None, password = None, request = None, form = None):
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
                if not dionysos_login(username, password, request, form):
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
            output = dionysos_login(username, password, request, form)
            if output:
                '''
                The credentials worked, try to create a user based on those credentials
                '''
                credentials = {
                        'username': username,
                        'password': password,
                }
                credentials['last_name'] = get_dionysos_last_name(output, form)
                credentials['first_name'] = get_dionysos_first_name(output, form)
                credentials['registration_number'] = get_dionysos_registration_number(output, form)
                credentials['semester'] = get_dionysos_semester(output, form)
                credentials['school'] = get_dionysos_school(output, form)
                credentials['introduction_year'] = get_dionysos_introduction_year(output, form)
                credentials['declaration'] = get_dionysos_declaration(username, password)
                #credentials['grades'] = get_dionysos_grades(username, password)
                user = add_student_to_db(credentials)
            else:
                return
        return user
