# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Authors(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.content_object.name

class Posts(models.Model):
    title = models.CharField(max_length = 500)
    pubdate = models.DateTimeField()
    creator = models.ForeignKey(Authors)
    unique = models.CharField(max_length = 255, unique = True)
    url = models.URLField()
    summary = models.TextField(null = True)
    enclosure = models.CharField("Attachment URL", max_length = 255, null = True)

    def __unicode__(self):
        return self.title

class Comments(models.Model):
    author = models.OneToOneField(User)
    post = models.ForeignKey(Posts)
    summary = models.TextField(null = True)
