# -*- coding: utf-8 -*-

from cronos.common.exceptions import CronosError
from cronos.common.log import log_extra_data
import logging
import requests

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def teilar_anon_login(url = None, request = None):
    '''
    Try to connect to *.teilar.gr and get the resulting HTML output.
    '''
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
    except Exception as error:
        '''
        *.teilar.gr is down
        '''
        logger_syslog.error(error, extra = log_extra_data(request))
        logger_mail.exception(error)
        site = url.split('/')[2]
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με το %s' % site)
    return response.text
