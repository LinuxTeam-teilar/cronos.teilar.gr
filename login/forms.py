# -*- coding: utf-8 -*-

from django import forms

class LoginForm(forms.Form):
		username = forms.CharField(max_length = 30, label = 'Όνομα Χρήστη:')
		password = forms.CharField(max_length = 30, widget = forms.PasswordInput(), label = 'Κωδικός Πρόσβασης:')
