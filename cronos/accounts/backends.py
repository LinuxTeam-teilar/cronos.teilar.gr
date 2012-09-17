# -*- coding: utf-8 -*-

from cronos.common.encryption import encrypt_password, decrypt_password
from cronos.common.exceptions import CronosError, LoginError
from cronos.common.log import log_extra_data
from cronos.common.get_admins import get_admins_usernames, get_admins_mails
from cronos.accounts.models import UserProfile
from cronos.accounts.get_student import *
from cronos.teilar.models import Departments
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

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
            skip dionysos authentication if the user is one of the listed ADMINS
            '''
            if user.username in get_admins_usernames():
                if user.check_password(password):
                    return user
            '''
            If the user is found in the DB, try to login with those
            credentials in dionysos.teilar.gr
            '''
            try:
                dionysos_auth_login(username, password)
            except LoginError:
                '''
                Authentication failed
                '''
                raise
            except CronosError:
                '''
                Connection issue with dionysos.teilar.gr. Try to authenticate
                with the password stored in the DB instead
                '''
                if password != decrypt_password(user.get_profile().dionysos_password):
                    raise LoginError
        except User.DoesNotExist:
            '''
            If the user is not in the DB, try to log in with his
            dionysos.teilar.gr account
            '''
            try:
                output, temp_tr = dionysos_auth_login(username, password, request, get_temp_tr = True)

                '''
                The credentials worked, try to create a user based on those credentials
                '''
                credentials = {'username': username, 'password': password}
                credentials['last_name'] = get_dionysos_last_name(temp_tr, request)
                credentials['first_name'] = get_dionysos_first_name(temp_tr, request)
                credentials['registration_number'] = get_dionysos_registration_number(temp_tr, request)
                credentials['semester'] = get_dionysos_semester(temp_tr, request)
                credentials['school'] = get_dionysos_school(temp_tr, request)
                credentials['introduction_year'] = get_dionysos_introduction_year(output, request)
                credentials['declaration'] = get_dionysos_declaration(username, password, request)
                #credentials['grades'] = get_dionysos_grades(username, password, request)
                try:
                    '''
                    Relate the webscraped school name with the one stored in the DB
                    '''
                    credentials['school'] = Departments.objects.get(name = credentials['school'])
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(request))
                    logger_mail.exception(error)
                    raise CronosError(u'Αδυναμία ανάκτησης της σχολής')
                user = self.add_student_to_db(credentials, request)
            except (CronosError, LoginError):
                raise
        return user

    def add_student_to_db(self, credentials, request):
        '''
        Adds a new user in the Database, along with the collected credentials from
        dionysos.teilar.gr
        '''
        user = User(
            username = credentials['username'],
            first_name = credentials['first_name'],
            last_name = credentials['last_name'],
            email = credentials['username'] + '@emptymail.com'
        )
        user.is_staff = False
        user.is_superuser = False
        try:
            user.save()
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(request))
            logger_mail.exception(error)
            raise CronosError(u'Σφάλμα αποθήκευσης βασικών στοιχείων χρήστη')
        '''
        Additional information are added in the userprofile table
        '''
        try:
            user_profile = UserProfile(
                user = user,
                dionysos_username = credentials['username'],
                dionysos_password = encrypt_password(credentials['password']),
                registration_number = credentials['registration_number'],
                semester = credentials['semester'],
                school = credentials['school'],
                introduction_year = credentials['introduction_year'],
                declaration = credentials['declaration'],
                #grades = credentials['grades'],
            )
            user_profile.save()
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(request))
            logger_mail.exception(error)
            raise CronosError(u'Σφάλμα αποθήκευσης πρόσθετων στοιχείων χρήστη')
        '''
        Everything went fine
        Notify admins about the new registration
        '''
        title = u'New user No.%s: %s' % (user.id, user.username)
        message = u'Name: %s %s\nDepartment: %s\nSemester: %s' % (
            user.first_name, user.last_name, user_profile.school, user_profile.semester
        )
        logger_syslog.info(title, extra = log_extra_data(request))
        try:
            send_mail(settings.EMAIL_SUBJECT_PREFIX + title, message,
                settings.SERVER_EMAIL, get_admins_mails())
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(request))
            logger_mail.exception(error)
        '''
        Return the new user object
        '''
        return user
