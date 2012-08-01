# -*- coding: utf-8 -*-

from django.db import models

class Announcements(models.Model):
    title = models.CharField("Title", max_length = 500)
    pubdate = models.DateTimeField(auto_now = True)
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
            return u'%s<br /><br /><a href="%s">%s</a><br /><br /> \
                    <a href="%s">Περισσότερα</a>' % (
                            self.description,
                            self.attachment_url,
                            self.attachment_text, self.url)
        else:
            return u'%s<br /><br /><a href="%s">Περισσότερα</a>' % (self.description, self.url)
