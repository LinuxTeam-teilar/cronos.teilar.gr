# -*- coding: utf-8 -*-

from django import forms

class MailForm(forms.Form):
	passed_id = forms.CharField(max_length = 100)
