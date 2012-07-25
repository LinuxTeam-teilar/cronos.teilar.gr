from django.db import models

class Faculties(models.Model):
    urlid = models.IntegerField(unique = True)
    name = models.CharField("Faculty name", max_length = 200)
    code = models.CharField("Faculty code", max_length = 10)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Lessons(models.Model):
    urlid = models.CharField(max_length = 10, unique = True)
    name = models.CharField("Lesson name", max_length = 200)
    teacher = models.CharField("Teacher's name", max_length = 200)
    faculty = models.ForeignKey(Faculties)
    ltype = models.CharField("Type of lesson", max_length = 50)
    deprecated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name
