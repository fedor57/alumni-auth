# -*- coding: utf-8 -*-

"""
Definition of forms.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

class CodeForm(forms.Form):
    code = forms.CharField(required=True)

class InviteForm(forms.Form):
    alumni_name = forms.CharField(max_length = 200, label='',
        widget=forms.TextInput(attrs={'class': 'alumni-select form-control', 'size': 200,
                                      'placeholder': 'Выберите имя и класс выпуска'}))

