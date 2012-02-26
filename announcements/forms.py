# -*- coding: utf-8 -*-

from django import forms

class AnnouncementForm(forms.Form):
    announceid = forms.CharField(max_length = 100)
