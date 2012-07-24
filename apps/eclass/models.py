from django.db import models

class Faculties(models.Model):
    urlid = models.IntegerField(unique = True)
    name = models.CharField("Faculty name", max_length = 200)
    code = models.CharField("Faculty code", max_length = 10)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
