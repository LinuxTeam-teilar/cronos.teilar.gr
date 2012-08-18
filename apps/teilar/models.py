from django.db import models

class Departments(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
#    email = models.EmailField(null = True)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Teachers(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    email = models.EmailField(null = True)
    department = models.ForeignKey(Departments)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
