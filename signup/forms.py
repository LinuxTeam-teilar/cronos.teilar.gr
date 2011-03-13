# -*- coding: utf-8 -*-

from django import forms

class SignupForm(forms.Form):
	dionysos_username = forms.CharField(max_length = 100, label = 'Όνομα Χρήστη από το dionysos:')
	dionysos_password = forms.CharField(max_length = 100, widget = forms.PasswordInput(), label = 'Κωδικός Πρόσβασης από το dionysos:')
	eclass_username = forms.CharField(max_length = 100, label = 'Όνομα Χρήστη από το e-class:', required = False)
	eclass_password = forms.CharField(max_length = 100, widget = forms.PasswordInput(), label = 'Κωδικός Πρόσβασης από το e-class:', required = False)
	webmail_username = forms.CharField(max_length = 100, label = 'Όνομα Χρήστη από το webmail:', required = False)
	webmail_password = forms.CharField(max_length = 100, widget = forms.PasswordInput(), label = 'Κωδικός Πρόσβασης από το webmail:', required = False)
	username = forms.CharField(max_length = 100, label = 'Όνομα Χρήστη για το cronos:')
	password1 = forms.CharField(max_length = 100, widget = forms.PasswordInput(), label = 'Κωδικός Πρόσβασης για το cronos:')
	password2 = forms.CharField(max_length = 100, widget = forms.PasswordInput(), label = 'Επαλήθευση Κωδικού Πρόσβασης:')
