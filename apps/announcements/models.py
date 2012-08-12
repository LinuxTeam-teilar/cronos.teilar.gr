# -*- coding: utf-8 -*-

from django.db import models

class Announcements(models.Model):
    title = models.CharField("Title", max_length = 500)
    pubdate = models.DateTimeField()
    creator = models.CharField(max_length = 200)
    unique = models.CharField(max_length = 250, unique = True)
    link = models.URLField()
    summary = models.TextField(null = True)
    enclosure = models.CharField("Attachment URL", max_length = 200, null = True)

    def __unicode__(self):
        return self.title
