# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import send_mail
import logging
#import traceback

def cronos_debug(msg, logfile):
    '''
    To be deprecated, along with the import logging and settings
    '''
    logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s: %(message)s', filename = settings.LOGDIR + logfile, filemode = 'a+')
    logging.debug(msg)

def mail_cronos_admin(title, message):
    '''
    Wrapper function of send_mail
    '''
    try:
        send_mail(title, message, 'notification@cronos.teilar.gr', ['cronos@teilar.gr'])
    except:
        pass

class CronosError(Exception):
    '''
    Custom Exception class
    '''
    def __init__(self, value):
        self.value = value
    def __unicode__(self):
        return repr(self.value)

def log_extra_data(request = None, form = None):
    '''
    Extra data needed by the custom formatter
    All values default to None
    '''
    log_extra_data = {
        'client_ip': request.META.get('REMOTE_ADDR','None') if request else '',
        'username': '',
    }
    if form:
        log_extra_data['username'] = form.data.get('username', 'None')
    else:
        try:
            if request.user.is_authenticated():
                '''
                Handle logged in users
                '''
                log_extra_data['username'] = request.user.name
            else:
                '''
                Handle anonymous users
                '''
                log_extra_data['username'] = 'Anonymous'
        except AttributeError:
            pass
    return log_extra_data
