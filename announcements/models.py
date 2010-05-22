# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher
from django.core.urlresolvers import reverse

class Id(models.Model):
	urlid = models.CharField("URL id", max_length = 30, unique = True)
	name = models.CharField("Teacher, School or Lesson name", max_length = 100)
	email = models.EmailField("Teacher's mail", null = True)
	department = models.CharField("Teacher's department", max_length = 100, null = True)

	def __unicode__(self):
		return self.name

class Announcements(models.Model):
	title = models.CharField("Title", max_length = 500)
	date_fetched = models.DateTimeField(auto_now = True)
	urlid = models.ForeignKey(Id)
	unique = models.CharField("Unique entry", max_length = 250, unique = True)
	url = models.URLField()
	description = models.TextField("Attachment Text", null = True)
	attachment_text = models.CharField("Attachment Text", max_length = 200, null = True)
	attachment_url = models.CharField("Attachment URL", max_length = 200, null = True)

	def date(self):
		return self.date_fetched

	def author(self):
		return self.urlid.name

	def get_absolute_url(self):
		return self.url

	def __unicode__(self):
		return self.title
	
	def body(self):	
		if (len(self.attachment_url) > 1):
			return u'%s<br /><br /><a href="%s">%s</a><br /><br /><a href="%s">Περισσότερα</a>' % (self.description, self.attachment_url, self.attachment_text, self.url)
		else:
			return u'%s<br /><br /><a href="%s">Περισσότερα</a>' % (self.description, self.url)
