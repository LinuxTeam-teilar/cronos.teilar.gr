from django.db import models

class Departments(models.Model):
    urlid = models.IntegerField(unique = True)
    name = models.CharField("Department name", max_length = 200)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Teachers(models.Model):
    urlid = models.IntegerField(unique = True)
    name = models.CharField("Teacher name", max_length = 100)
    email = models.EmailField("Teacher's mail", null = True)
    department = models.ForeignKey(Departments)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name


