# -*- coding: utf-8 -*-

from django import forms

class DeclarationForm(forms.Form):
    declaration = forms.CharField(required = False, widget = forms.HiddenInput())
