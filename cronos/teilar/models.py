from django.db import models

class Departments(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    email = models.EmailField(null = True)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name

class Teachers(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    email = models.EmailField(null = True)
    department = models.ForeignKey(Departments)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name

class Websites(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    rss = models.URLField()
    email = models.EmailField(null = True)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name

class EclassFaculties(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 255)
    code = models.CharField(max_length = 10)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name

class EclassLessons(models.Model):
    url = models.URLField(unique = True)
    name = models.CharField(max_length = 500)
    teacher = models.CharField(max_length = 500)
    faculty = models.ForeignKey(EclassFaculties)
    ltype = models.CharField(max_length = 100)
    is_active = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name
