# -*- coding: utf-8 -*-

from django.conf import settings

def log_extra_data(additional = None):
    '''
    Extra data needed by the custom formatter
    * If the additional argument is a string or unicode, then its value is printed
    in the log.
    * If the additiona argument is the request, then from the request it
    prints the client IP and username if applicable.
    '''
    log_extra_data = {
        'client_ip': '',
        'id_name': '',
    }
    if type(additional) == str or type(additional) == unicode:
        log_extra_data['id_name'] = additional
    else:
        request = additional
        if request.META:
            log_extra_data['client_ip'] = request.META.get('REMOTE_ADDR', 'None')
        try:
            if request.user.is_authenticated():
                '''
                Handle logged in users
                '''
                log_extra_data['id_name'] = request.user.name
        except AttributeError:
                pass
    return log_extra_data
