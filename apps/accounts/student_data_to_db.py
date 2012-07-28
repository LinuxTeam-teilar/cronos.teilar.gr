# -*- coding: utf-8 -*-

from apps import CronosError, log_extra_data
from apps.accounts.models import UserProfile
from apps.accounts.encryption import encrypt_password
from apps.teilar.models import Departments
from django.contrib.auth.models import User
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def add_student_to_db(credentials):
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
        logger_syslog.error(error, extra = log_extra_data(username = credentials['username']))
        logger_mail.exception(error)
        raise CronosError(u'Σφάλμα αποθήκευσης χρήστη')
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
            school = Departments.objects.get(name = credentials['school']),
            introduction_year = credentials['introduction_year'],
            declaration = credentials['declaration'],
#           grades = credentials['grades'],
        )
        user_profile.save()
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(username = credentials['username']))
        logger_mail.exception(error)
        raise CronosError(u'Σφάλμα αποθήκευσης χρήστη')
    '''
    If everything went fine, return the new user
    '''
    return user
