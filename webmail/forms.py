# -*- coding: utf-8 -*-

from django import forms

class MailForm(forms.Form):
    passed_id = forms.CharField(widget = forms.HiddenInput())
