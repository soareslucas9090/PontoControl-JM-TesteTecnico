import re

from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    cpf = forms.CharField(widget=forms.TextInput(), label="CPF")
    password = forms.CharField(widget=forms.PasswordInput(), label="Senha")

    def clean_cpf(self):
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11:
            raise ValidationError("O CPF deve conter 11 dígitos")

        return cpf
