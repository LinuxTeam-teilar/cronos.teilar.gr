# -*- coding: utf-8 -*-

from django import forms

class RecoverForm(forms.Form):
	username = forms.CharField(label = 'Όνομα Χρήστη', max_length = 100)
