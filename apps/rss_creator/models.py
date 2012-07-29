from django.db import models

class AnnouncementsTeilar(models.Model):
    urlid = models.IntegerField(unique = True)
    author = models.CharField(max_length = 200)
    title = models.CharField(max_length = 300)
    date = models.DateField()
    summary = models.TextField(null = True, blank = True)
    attachment = models.URLField(null = True, blank = True)
