import re

from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    cpf = forms.CharField(widget=forms.TextInput(), label="CPF")
    password = forms.CharField(widget=forms.PasswordInput(), label="Senha")

    def clean_cpf(self):
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf


class EmpresaForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput(), label="Nome")
    endereco = forms.CharField(widget=forms.TextInput(), label="Endereço")


class FuncionarioForm(forms.Form):
    nome = forms.CharField(widget=forms.TextInput(), label="Nome")
    cpf = forms.CharField(widget=forms.TextInput(), label="CPF")
    email = forms.EmailField(widget=forms.EmailInput(), label="Email")
    senha = forms.CharField(widget=forms.TextInput(), label="Senha")

    def clean_cpf(self):
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf

    def clean_senha(self):
        senha = str(self.cleaned_data.get("senha"))

        if len(senha) < 8:
            raise ValidationError("A senha deve conter no mínimo 8 caracteres")

        return senha


class PontoForm(forms.Form):
    CPF = forms.CharField(widget=forms.TextInput(), label="CPF")

    def clean_CPF(self):
        cpf = str(self.cleaned_data.get("CPF"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf
