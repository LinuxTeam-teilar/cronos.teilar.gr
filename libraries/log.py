# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.core.mail import send_mail

def cronosDebug(msg, logfile):
	logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s: %(message)s', filename = settings.LOGDIR + logfile, filemode = 'a+')
	logging.debug(msg)

def mailCronosAdmin(title, message):
	try:
		send_mail(title, message, 'notification@cronos.teilar.gr', ['cronos@teilar.gr'])
	except:
		pass

class CronosError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
