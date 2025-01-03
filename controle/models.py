from datetime import datetime

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models
from django.db.utils import IntegrityError
from django.utils.timezone import now


class Endereco(models.Model):
    """
    Modelo que representa um endereço.

    Atributos:
        logradouro (str): Logradouro do endereço.
        numero (int): Número do endereço.
        complemento (str): Complemento do endereço.
        bairro (str): Bairro do endereço.
        cidade (str): Cidade do endereço.
        estado (str): Estado do endereço.
        cep (str): CEP do endereço.
    """

    logradouro = models.CharField(max_length=255)
    numero = models.IntegerField()
    complemento = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, null=True)
    estado = models.CharField(max_length=255)
    cep = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.logradouro}, n° {self.numero}, {self.complemento}, {self.bairro}, {self.cidade}, {self.estado}, {self.cep}"


class Empresa(models.Model):
    """
    Modelo que representa uma empresa.

    Atributos:
        nome (str): Nome da empresa.
        endereco (Endereco): Endereço da empresa.
    """

    nome = models.CharField(max_length=255)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.DO_NOTHING, related_name="empresa"
    )

    def __str__(self):
        """
        Retorna a representação textual da empresa.

        Retorna:
            str: Nome da empresa.
        """
        return self.nome


class UserManager(BaseUserManager):
    """
    Gerenciador de usuários para criação de usuários comuns e superusuários.

    Métodos:
        create_user: Cria um usuário comum.
        create_superuser: Cria um superusuário.
    """

    def create_user(self, cpf, password=None, **extra_fields):
        """
        Cria e salva um usuário comum.

        Parâmetros:
            cpf (str): CPF do usuário.
            password (str, opcional): Senha do usuário.
            extra_fields (dict): Campos adicionais para o usuário.

        Retorna:
            Usuario: Usuário criado.

        Lança:
            ValueError: Se o CPF for inválido ou se faltarem campos obrigatórios.
        """
        if not cpf:
            raise ValueError("O Usuário precisa ter um CPF válido")
        if not cpf.isnumeric() or len(cpf) != 11:
            raise ValueError("O CPF precisa ter 11 dígitos numéricos")

        if extra_fields.get("is_superuser", False):
            extra_fields["is_staff"] = True
        else:
            if not extra_fields.get("funcionario", None):
                raise ValueError("Usuários precisam estar associados a um funcionário")

        user = self.model(cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, password=None, **extra_fields):
        """
        Cria e salva um superusuário.

        Parâmetros:
            cpf (str): CPF do superusuário.
            password (str, opcional): Senha do superusuário.
            extra_fields (dict): Campos adicionais para o superusuário.

        Retorna:
            Usuario: Superusuário criado.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(cpf=cpf, password=password, **extra_fields)
        permissions = Permission.objects.all()
        user.user_permissions.set(permissions)

        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo que representa um usuário do sistema.

    Atributos:
        cpf (str): CPF do usuário.
        funcionario (Funcionario): Referência ao funcionário associado.
        is_staff (bool): Indica se o usuário é membro do staff.
        is_superuser (bool): Indica se o usuário é superusuário.
        is_active (bool): Indica se o usuário está ativo.
        groups (Group): Grupos associados ao usuário.
        user_permissions (Permission): Permissões associadas ao usuário.
    """

    cpf = models.CharField(max_length=11, unique=True)
    funcionario = models.ForeignKey(
        "Funcionario", on_delete=models.CASCADE, related_name="usuarios", null=True
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, verbose_name="É superusuário")
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        verbose_name="Grupos",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        verbose_name="Permissões",
        blank=True,
    )

    USERNAME_FIELD = "cpf"

    objects = UserManager()

    def __str__(self):
        """
        Retorna a representação textual do usuário.

        Retorna:
            str: CPF do usuário.
        """
        return self.cpf


class Funcionario(models.Model):
    """
    Modelo que representa um funcionário.

    Atributos:
        nome (str): Nome do funcionário.
        email (str): Email do funcionário.
        empresa (Empresa): Referência à empresa associada.
    """

    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="funcionarios"
    )

    def criar_usuario(self, cpf: str, senha: str) -> Usuario | str:
        """
        Cria um usuário associado ao funcionário.

        Parâmetros:
            cpf (str): CPF do usuário.
            senha (str): Senha do usuário.

        Retorna:
            Usuario | str: Usuário criado ou mensagem de erro.
        """
        try:
            usuario = Usuario.objects.create_user(
                cpf=cpf, password=senha, funcionario=self
            )
        except IntegrityError:
            usuario = Usuario.objects.get(cpf=cpf)
            return f"Já existe um funcionário registrado com este CPF na empresa {usuario.funcionario.empresa}"
        return usuario

    def __str__(self):
        """
        Retorna a representação textual do funcionário.

        Retorna:
            str: Nome do funcionário.
        """
        return self.nome


class Ponto(models.Model):
    """
    Modelo que representa um ponto de registro de entrada e saída.

    Atributos:
        funcionario (Funcionario): Funcionário relacionado ao ponto.
        data (date): Data do ponto.
        entrada (time): Horário de entrada.
        saida (time): Horário de saída.
    """

    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name="pontos"
    )
    data = models.DateField(default=now)
    entrada = models.TimeField(default=now)
    saida = models.TimeField(null=True)

    def horas_trabalhadas(self) -> dict[str, str]:
        """
        Calcula as horas trabalhadas com base na entrada e saída.

        Retorna:
            dict[str, str]: Horas e minutos trabalhados.
        """
        entrada_datetime = datetime.combine(self.data, self.entrada)

        if self.saida:
            saida_datetime = datetime.combine(self.data, self.saida)
            delta = saida_datetime - entrada_datetime
        else:
            delta = datetime.now() - entrada_datetime

        horas, resto = divmod(delta.total_seconds(), 3600)
        minutos = resto // 60

        return {
            "horas_trabalhadas": f"{horas} horas e {minutos} minutos.",
        }

    def __str__(self):
        """
        Retorna a representação textual do ponto.

        Retorna:
            str: Descrição do ponto.
        """
        return f"Ponto de {self.funcionario.nome} - {self.data}"
