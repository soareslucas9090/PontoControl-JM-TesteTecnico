from datetime import datetime

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models
from django.utils.timezone import now


class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.TextField()

    def __str__(self):
        return self.nome


class UserManager(BaseUserManager):
    def create_user(
        self,
        cpf,
        password=None,
        **extra_fields,
    ):
        if not cpf:
            raise ValueError("O Usuário precisa ter um CPF válido")
        if not cpf.isnumeric() or len(cpf) != 11:
            raise ValueError(f"O CPF precisa ter 11 dígitos numéricos")

        if extra_fields.get("is_superuser", False) is True:
            extra_fields["is_staff"] = True
        else:
            if not extra_fields.get("funcionario", None):
                raise ValueError(f"Usuarios precisam estar associados a um funcionario")

        user = self.model(
            cpf=cpf,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        cpf,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(
            cpf=cpf,
            password=password,
            **extra_fields,
        )

        permissions = Permission.objects.all()
        user.user_permissions.set(permissions)

        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(max_length=11, unique=True)
    funcionario = models.ForeignKey(
        "Funcionario", on_delete=models.CASCADE, related_name="usuarios", null=True
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, verbose_name="É super usuário")
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        verbose_name=("Grupos"),
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        verbose_name=("Permissões"),
        blank=True,
    )

    USERNAME_FIELD = "cpf"

    objects = UserManager()

    def __str__(self):
        return self.cpf


class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="funcionarios"
    )

    def criar_usuario(self, cpf: str, senha: str) -> Usuario:
        usuario = Usuario.objects.create_user(
            cpf=cpf,
            password=senha,
            funcionario=self,
        )
        return usuario

    def __str__(self):
        return self.nome


class Ponto(models.Model):
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name="pontos"
    )
    data = models.DateField(default=now)
    entrada = models.TimeField(default=now)
    saida = models.TimeField(null=True)

    def horas_trabalhadas(self) -> dict[str, str | datetime]:
        entrada_datetime = datetime.combine(self.data, self.entrada)

        if self.saida:
            saida_datetime = datetime.combine(self.data, self.saida)
            delta = saida_datetime - entrada_datetime

            horas, resto = divmod(delta.total_seconds(), 3600)
            minutos = resto // 60

            return {
                "status": "Ponto Fechado",
                "horas_trabalhadas": f"{horas} horas e {minutos} minutos.",
            }
        else:
            horas_corridas = datetime.now() - entrada_datetime
            return {"status": "Ponto Aberto", "horas_corridas": horas_corridas}

    def __str__(self):
        return f"Ponto de {self.funcionario.nome} - {self.data}"
