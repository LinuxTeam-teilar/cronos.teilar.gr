from cronos.teilar.models import Departments, Teachers, EclassLessons, Websites, Blogs
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key = True, unique = True)
    dionysos_username = models.CharField(max_length = 15, unique = True)
    dionysos_password = models.CharField(max_length = 30)
    eclass_username = models.CharField(max_length = 30, null = True, blank = True)
    eclass_password = models.CharField(max_length = 30, null = True, blank = True)
    introduction_year = models.CharField(max_length = 5)
    registration_number = models.CharField(max_length = 8)
    school = models.ForeignKey(Departments)
    semester = models.CharField(max_length = 2)
    webmail_username = models.CharField(max_length = 30, null = True, blank = True)
    webmail_password = models.CharField(max_length = 30, null = True, blank = True)
    following_teachers = models.ManyToManyField(Teachers)
    following_websites = models.ManyToManyField(Websites)
    following_blogs = models.ManyToManyField(Blogs)
    following_eclass_lessons = models.ManyToManyField(EclassLessons)
    declaration = models.TextField(null = True, blank = True)
    grades = models.TextField(null = True, blank = True)

    def __unicode__(self):
        return self.user.username
