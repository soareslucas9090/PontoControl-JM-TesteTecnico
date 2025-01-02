from django.apps import AppConfig
from django.db import OperationalError
from django.db.models.signals import post_migrate
from datetime import time, date


class ControleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "controle"

    def ready(self):
        from .models import Empresa, Usuario, Funcionario, Ponto

        post_migrate.connect(criar_empresas_padroes, sender=self)
        post_migrate.connect(criar_usuario_padrao, sender=self)
        post_migrate.connect(criar_funcionarios_padroes, sender=self)
        post_migrate.connect(criar_pontos_padroes, sender=self)


def criar_empresas_padroes(sender, **kwargs):
    Empresa = sender.get_model("Empresa")

    try:
        Empresa.objects.create(
            nome="Dois Irmãos - Supermercados MATRIZ",
            endereco="Rua Projetada X nº 400, Bairro Santo Antonio, Teresina-PI",
        )
        Empresa.objects.create(
            nome="Dois Irmãos - Supermercados FL 01",
            endereco="Rua Santa Ana nº 123, Bairro Tulipa, São Luiz-MA",
        )

        print("Criação de Empresas bem sucedida!")
    except OperationalError:
        print("Não foi possível realizar migração de dados de Empresas")
        pass


def criar_usuario_padrao(sender, **kwargs):
    Usuario = sender.get_model("Usuario")

    try:
        Usuario.objects.create_superuser(cpf="12345678910", password="12345678910")

        print("Criação de Gestor bem sucedida!")
    except OperationalError:
        print("Não foi possível realizar migração de dados do Usuario")
        pass


def criar_funcionarios_padroes(sender, **kwargs):
    Funcionario = sender.get_model("Funcionario")
    Empresa = sender.get_model("Empresa")

    try:
        empresa1 = Empresa.objects.get(nome="Dois Irmãos - Supermercados MATRIZ")
        empresa2 = Empresa.objects.get(nome="Dois Irmãos - Supermercados FL 01")

        funcionario = Funcionario.objects.create(
            nome="Carlos Eduardo", email="carlos.eduardo@emp1.com", empresa=empresa1
        )
        funcionario.criar_usuario("22222222222", "22222222222")

        funcionario = Funcionario.objects.create(
            nome="Maria Lúcia", email="maria.lucia@emp1.com", empresa=empresa1
        )
        funcionario.criar_usuario("33333333333", "12345678")

        funcionario = Funcionario.objects.create(
            nome="Antonio Soares", email="antonio.soares@emp1.com", empresa=empresa1
        )
        funcionario.criar_usuario("44444444444", "12345678")

        funcionario = Funcionario.objects.create(
            nome="Eduarda Soares", email="eduarda.soares@emp2.com", empresa=empresa2
        )
        funcionario.criar_usuario("55555555555", "12345678")

        funcionario = Funcionario.objects.create(
            nome="Joel Menezes", email="joel.menezes@emp2.com", empresa=empresa2
        )
        funcionario.criar_usuario("66666666666", "12345678")

        print("Criação de Funcionários bem sucedida!")
    except OperationalError:
        print("Não foi possível realizar migrate de dados de Usuarios")
        pass


def criar_pontos_padroes(sender, **kwargs):
    Ponto = sender.get_model("Ponto")
    Funcionario = sender.get_model("Funcionario")

    try:
        fun = Funcionario.objects.get(email="carlos.eduardo@emp1.com")
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 2),
            entrada=time(9, 1, 15),
            saida=time(15, 9, 55),
        )
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 3),
            entrada=time(9, 2, 12),
            saida=time(15, 2, 11),
        )

        fun = Funcionario.objects.get(email="maria.lucia@emp1.com")
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 2),
            entrada=time(9, 4, 53),
            saida=time(15, 1, 1),
        )
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 3),
            entrada=time(9, 7, 13),
            saida=time(15, 0, 53),
        )

        fun = Funcionario.objects.get(email="antonio.soares@emp1.com")
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 2),
            entrada=time(9, 3, 15),
            saida=time(15, 3, 42),
        )
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 3),
            entrada=time(9, 1, 12),
            saida=time(15, 7, 11),
        )

        fun = Funcionario.objects.get(email="eduarda.soares@emp2.com")
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 2),
            entrada=time(9, 5, 15),
            saida=time(15, 2, 55),
        )
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 3),
            entrada=time(9, 2, 12),
            saida=time(15, 2, 11),
        )

        fun = Funcionario.objects.get(email="joel.menezes@emp2.com")
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 2),
            entrada=time(9, 8, 19),
            saida=time(15, 2, 55),
        )
        Ponto.objects.create(
            funcionario=fun,
            data=date(2025, 1, 3),
            entrada=time(9, 2, 12),
            saida=time(15, 7, 11),
        )

        print("Criação de Pontos bem sucedida!")
    except:
        print("Não foi possível realizar migrate de dados de Usuarios")
        pass
