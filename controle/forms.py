import re

from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    """
    Formulário para autenticação de usuários.

    Campos:
        cpf (CharField): CPF do usuário.
        password (CharField): Senha do usuário.

    Métodos:
        clean_cpf(): Valida o campo CPF.
    """

    cpf = forms.CharField(widget=forms.TextInput(), label="CPF")
    password = forms.CharField(widget=forms.PasswordInput(), label="Senha")

    def clean_cpf(self):
        """
        Valida o CPF, garantindo que contenha apenas 11 dígitos numéricos.

        Retorna:
            str: CPF validado.

        Lança:
            ValidationError: Se o CPF não atender aos critérios.
        """
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf


class EmpresaForm(forms.Form):
    """
    Formulário para cadastro de empresas.

    Campos:
        nome (CharField): Nome da empresa.
        endereco (CharField): Endereço da empresa.
    """

    nome = forms.CharField(widget=forms.TextInput(), label="Nome")
    endereco = forms.CharField(widget=forms.Textarea, label="Endereço")


class FuncionarioForm(forms.Form):
    """
    Formulário para cadastro de funcionários.

    Campos:
        nome (CharField): Nome do funcionário.
        cpf (CharField): CPF do funcionário.
        email (EmailField): Email do funcionário.
        senha (CharField): Senha do funcionário.

    Métodos:
        clean_cpf(): Valida o campo CPF.
        clean_senha(): Valida o campo senha.
    """

    nome = forms.CharField(widget=forms.TextInput(), label="Nome")
    cpf = forms.CharField(widget=forms.TextInput(), label="CPF")
    email = forms.EmailField(widget=forms.EmailInput(), label="Email")
    senha = forms.CharField(widget=forms.TextInput(), label="Senha")

    def clean_cpf(self):
        """
        Valida o CPF, garantindo que contenha apenas 11 dígitos numéricos.

        Retorna:
            str: CPF validado.

        Lança:
            ValidationError: Se o CPF não atender aos critérios.
        """
        cpf = str(self.cleaned_data.get("cpf"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf

    def clean_senha(self):
        """
        Valida a senha, garantindo que tenha no mínimo 8 caracteres.

        Retorna:
            str: Senha validada.

        Lança:
            ValidationError: Se a senha não atender aos critérios.
        """
        senha = str(self.cleaned_data.get("senha"))

        if len(senha) < 8:
            raise ValidationError("A senha deve conter no mínimo 8 caracteres")

        return senha


class PontoForm(forms.Form):
    """
    Formulário para registro de ponto.

    Campos:
        CPF (CharField): CPF do funcionário.

    Métodos:
        clean_CPF(): Valida o campo CPF.
    """

    CPF = forms.CharField(widget=forms.TextInput(), label="CPF")

    def clean_CPF(self):
        """
        Valida o CPF, garantindo que contenha apenas 11 dígitos numéricos.

        Retorna:
            str: CPF validado.

        Lança:
            ValidationError: Se o CPF não atender aos critérios.
        """
        cpf = str(self.cleaned_data.get("CPF"))

        cpf = re.sub("[^0-9]", "", cpf)

        if len(cpf) != 11 or not cpf.isnumeric():
            raise ValidationError("O CPF deve conter 11 dígitos numéricos")

        return cpf


class FiltroPontoForm(forms.Form):
    """
    Formulário para filtrar pontos por intervalo de datas.

    Campos:
        data_inicial (DateField): Data inicial do intervalo.
        data_final (DateField): Data final do intervalo.

    Métodos:
        clean(): Valida o intervalo de datas.
    """

    data_inicial = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Data Inicial"
    )
    data_final = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Data Final"
    )

    def clean(self):
        """
        Valida o intervalo de datas, garantindo que a data inicial não seja maior que a data final.

        Retorna:
            dict: Dados validados.

        Lança:
            ValidationError: Se a data inicial for maior que a data final.
        """
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get("data_inicial")
        data_final = cleaned_data.get("data_final")

        if data_inicial and data_final:
            if data_inicial > data_final:
                raise ValidationError(
                    "A data inicial não pode ser maior que a data final."
                )

        return cleaned_data
