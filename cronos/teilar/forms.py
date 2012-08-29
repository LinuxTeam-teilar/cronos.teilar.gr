# -*- coding: utf-8 -*-

from django import forms

class LibraryForm(forms.Form):
    search = forms.CharField(label = 'Αναζήτηση', max_length = 100)
