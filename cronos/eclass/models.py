from django.db import models

class Faculties(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    code = models.CharField(max_length = 10)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Lessons(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 500)
    teacher = models.CharField(max_length = 500)
    faculty = models.ForeignKey(Faculties)
    ltype = models.CharField(max_length = 100)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
