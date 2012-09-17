# -*- coding: utf-8 -*-

class CronosError(Exception):
    '''
    Custom Exception class for general errors
    '''
    def __init__(self, value):
        self.value = value
    def __unicode__(self):
        return repr(self.value)
