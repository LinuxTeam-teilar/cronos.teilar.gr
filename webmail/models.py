# -*- coding: utf-8 -*-

from django.db import models

class Link(models.Model) :
  url = models.URLField(unique=True)
