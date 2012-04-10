# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from cronos.accounts.models import UserProfile
from cronos.announcements.models import Id
from cronos.accounts.encryption import encrypt_password
from cronos.libraries.log import CronosError, log_extra_data
import logging

logger = logging.getLogger('cronos')

def add_new_student(credentials):
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
        logger.error(error, extra = log_extra_data())
        raise CronosError(u'Σφάλμα αποθήκευσης χρήστη')
    '''
    Get the school ID from the Id table, instead of storing the full school name
    '''
    for item in Id.objects.filter(name__exact = credentials['school']):
        cid = str(item.urlid)
    '''
    Additional information are added in the userprofile table
    '''
    user_profile = UserProfile(
        user = user,
        dionysos_username = credentials['username'],
        dionysos_password = encrypt_password(credentials['password']),
        registration_number = credentials['registration_number'],
        semester = credentials['semester'],
        school = cid,
        introduction_year = credentials['introduction_year'],
        declaration = credentials['declaration'],
#        grades = credentials['grades'],
    )
    try:
        user_profile.save()
    except Exception as error:
        logger.error(error, extra = log_extra_data())
        raise CronosError(u'Σφάλμα αποθήκευσης χρήστη')
    '''
    If everything went fine, return the new user
    '''
    return user
