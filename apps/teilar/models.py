from django.db import models

class Departments(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField("Department name", max_length = 200)
#    email = models.EmailField("Department's mail", null = True)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Teachers(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField("Teacher name", max_length = 100)
    email = models.EmailField("Teacher's mail", null = True)
    department = models.ForeignKey(Departments)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
