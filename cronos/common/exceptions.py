# -*- coding: utf-8 -*-

class CronosError(Exception):
    '''
    Custom Exception class for general errors
    '''
    def __init__(self, value):
        self.value = value
    def __unicode__(self):
        return repr(self.value)

class LoginError(Exception):
    '''
    Custom Exception class for login failures
    due to wrong credentials
    '''
    def __init__(self):
        self.value = u'Λάθος στοιχεία'
    def __unicode__(self):
        return repr(self.value)
