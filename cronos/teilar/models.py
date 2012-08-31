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

class Websites(models.Model):
    rss = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    url = models.URLField()
    email = models.EmailField(null = True)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class EclassFaculties(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    code = models.CharField(max_length = 10)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class EclassLessons(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 500)
    teacher = models.CharField(max_length = 500)
    faculty = models.ForeignKey(EclassFaculties)
    ltype = models.CharField(max_length = 100)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
