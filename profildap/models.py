# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class LdapProfile(models.Model):
	user = models.ForeignKey(User, unique = True)
	dionysos_username = models.CharField(max_length = 15, unique = True)
	dionysos_password = models.CharField(max_length = 30)
	eclass_username = models.CharField(max_length = 30, null = True)
	eclass_password = models.CharField(max_length = 30, null = True)
	eclass_lessons = models.TextField(null = True)
	introduction_year = models.CharField(max_length = 5)
	registration_number = models.CharField(max_length = 8)
	school = models.CharField(max_length = 4)
	semester = models.CharField(max_length = 2)
	webmail_username = models.CharField(max_length = 30, null = True)
	webmail_password = models.CharField(max_length = 30, null = True)
	teacher_announcements = models.TextField(null = True)
	other_announcements = models.TextField(null = True)
	declaration = models.TextField(null = True)
