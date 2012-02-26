# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.user.models import UserProfile
from django import forms
from django.db.models import Q


class CronosForm(forms.Form):
    old_password = forms.CharField(max_length = 30, widget = forms.PasswordInput(), label = 'Παλιός Κωδικός:')
    password1 = forms.CharField(max_length = 30, widget = forms.PasswordInput(), label = 'Νέος Κωδικός:')
    password2 = forms.CharField(max_length = 30, widget = forms.PasswordInput(), label = 'Επαλήθευση Νέου Κωδικού:')

class DionysosForm(forms.Form):
    dionysos_username = forms.CharField(max_length = 30)
    dionysos_password = forms.CharField(max_length = 30, widget = forms.PasswordInput())

class Eclass1Form(forms.Form):
    eclass_username = forms.CharField(max_length = 30)
    eclass_password = forms.CharField(max_length = 30, widget = forms.PasswordInput())

class WebmailForm(forms.Form):
    webmail_username = forms.CharField(max_length = 30)
    webmail_password = forms.CharField(max_length = 30, widget = forms.PasswordInput())

class EmailForm(forms.Form):
    email = forms.EmailField()

class DeclarationForm(forms.Form):
    declaration = forms.CharField(widget = forms.HiddenInput())

class GradesForm(forms.Form):
    grades = forms.CharField(widget = forms.HiddenInput())

class Eclass2Form(forms.Form):
    eclass_lessons = forms.CharField(widget = forms.HiddenInput())
