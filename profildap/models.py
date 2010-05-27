# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class LdapProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	dionysos_username = models.CharField(max_length=100, blank=True)
