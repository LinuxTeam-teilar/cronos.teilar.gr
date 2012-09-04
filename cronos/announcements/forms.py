from django import forms

class PostForm(forms.Form):
    post_id = forms.HiddenInput()
