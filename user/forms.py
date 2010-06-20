# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.user.models import LdapProfile
from django import forms
from django.db.models import Q


class TeacherAnnouncementsForm(forms.ModelForm):
	teacher_announcements = forms.ModelMultipleChoiceField(queryset = Id.objects.filter(urlid__startswith = 'pid').order_by('name'), widget = forms.SelectMultiple)

	class Meta:
		model = LdapProfile
		exclude = ['user', 'declaration', 'dionysos_username', 'dionysos_password', 'eclass_username', 'eclass_password', 'eclass_lessons', 'introduction_year', 'registration_number', 'school', 'semester', 'webmail_username', 'webmail_password', 'teacher_announcements', 'other_announcements']
		fields = ['teacher_announcements']

'''class OtherAnnouncementsForm(forms.ModelForm):
	other_announcements = forms.ModelMultipleChoiceField(queryset = Id.objects.filter(Q(urlid__startswith = 'cid5') | Q(urlid__exact = 'cid0')).order_by('name'), widget = MultipleSelectWithPop)

	class Meta:
		model = LdapProfile
		exclude = ['user', 'declaration', 'dionysos_username', 'dionysos_password', 'eclass_username', 'eclass_password', 'eclass_lessons', 'introduction_year', 'registration_number', 'school', 'semester', 'webmail_username', 'webmail_password', 'teacher_announcements', 'other_announcements']'''

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
