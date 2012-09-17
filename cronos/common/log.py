# -*- coding: utf-8 -*-

from django.conf import settings

def log_extra_data(id_name = None, request = None):
    '''
    Extra data needed by the custom formatter
    All values default to None
    It provides three data: client_ip, username and cronjob name
    Username can be passed directly as argument, or it can be retrieved by
    either the request var or the form
    '''
    log_extra_data = {
        'client_ip': request.META.get('REMOTE_ADDR','None') if request else '',
        'id_name': id_name if id_name else '',
    }
    if not id_name:
        try:
            if request.user.is_authenticated():
                '''
                Handle logged in users
                '''
                log_extra_data['id_name'] = request.user.name
        except AttributeError:
                pass
    return log_extra_data
