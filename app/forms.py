# -*- coding: utf-8 -*-

"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class CodeForm(forms.Form):
    code = forms.CharField(required=True)

class InviteForm(forms.Form):
    alumni_name = forms.CharField(label='Выберите выпускника:', max_length = 200, widget=forms.TextInput(attrs={'class': 'alumni-select'}))

