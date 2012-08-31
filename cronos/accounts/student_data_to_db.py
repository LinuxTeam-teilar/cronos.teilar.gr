# -*- coding: utf-8 -*-

from cronos.common.log import CronosError, log_extra_data
from cronos.accounts.models import UserProfile
from cronos.accounts.encryption import encrypt_password
from cronos.teilar.models import Departments
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def add_student_to_db(credentials, request):
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
        logger_syslog.error(error, extra = log_extra_data(credentials['username'], request))
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
            school = Departments.objects.get(name = credentials['school']),
            introduction_year = credentials['introduction_year'],
            declaration = credentials['declaration'],
            #grades = credentials['grades'],
        )
        user_profile.save()
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(credentials['username'], request))
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
    logger_syslog.info(title, extra = log_extra_data(user.username, request))
    try:
        send_mail(settings.EMAIL_SUBJECT_PREFIX + title, message,
            settings.SERVER_EMAIL, [settings.ADMINS[0][1]])
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(user.username, request))
        logger_mail.exception(error)
    '''
    Return the new user object
    '''
    return user
