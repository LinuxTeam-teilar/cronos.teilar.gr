# -*- coding: utf-8 -*-

from cronos.announcements.models import *
from cronos.user.widgets import *
from cronos.user.models import LdapProfile
from django import forms
from django.db.models import Q


class TeacherAnnouncementsForm(forms.ModelForm):
	teacher_announcements = forms.ModelMultipleChoiceField(queryset = Id.objects.filter(urlid__startswith = 'pid').order_by('name'), widget = forms.SelectMultiple)

	class Meta:
		model = LdapProfile
		exclude = ['user', 'declaration', 'dionysos_username', 'dionysos_password', 'eclass_username', 'eclass_password', 'eclass_lessons', 'introduction_year', 'registration_number', 'school', 'semester', 'webmail_username', 'webmail_password', 'teacher_announcements', 'other_announcements']
		fields = ['teacher_announcements']

class OtherAnnouncementsForm(forms.ModelForm):
	other_announcements = forms.ModelMultipleChoiceField(queryset = Id.objects.filter(Q(urlid__startswith = 'cid5') | Q(urlid__exact = 'cid0')).order_by('name'), widget = MultipleSelectWithPop)

	class Meta:
		model = LdapProfile
		exclude = ['user', 'declaration', 'dionysos_username', 'dionysos_password', 'eclass_username', 'eclass_password', 'eclass_lessons', 'introduction_year', 'registration_number', 'school', 'semester', 'webmail_username', 'webmail_password', 'teacher_announcements', 'other_announcements']
