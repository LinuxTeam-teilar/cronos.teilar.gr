# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class LdapProfile(models.Model):
	user = models.ForeignKey(User, unique = True)
	dionysos_username = models.CharField(max_length = 100, unique = True)
	dionysos_password = models.CharField(max_length = 100)
	eclass_username = models.CharField(max_length = 100, blank = True)
	eclass_password = models.CharField(max_length = 100, blank = True)
	eclass_lessons = models.TextField(blank = True)
	introduction_year = models.CharField(max_length = 5)
	registration_number = models.CharField(max_length = 10)
	school = models.CharField(max_length = 4)
	semester = models.CharField(max_length = 3)
	webmail_username = models.CharField(max_length = 100, blank = True)
	webmail_password = models.CharField(max_length = 100, blank = True)
	teacher_announcements = models.TextField(blank = True)
	other_announcements = models.TextField(blank = True)
	declaration = models.TextField()
