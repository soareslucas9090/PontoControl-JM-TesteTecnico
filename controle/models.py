from django.db import models
from django.utils.timezone import now
import datetime


class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.TextField()

    def __str__(self):
        return self.nome


class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="funcionarios"
    )

    def __str__(self):
        return self.nome


class Ponto(models.Model):
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name="pontos"
    )
    data = models.DateField(default=now)
    entrada = models.TimeField()
    saida = models.TimeField(null=True)

    def horas_trabalhadas(self) -> dict[str, str | datetime.timedelta]:
        delta = None
        entrada_datetime = datetime.combine(self.data, self.entrada)

        if self.saida:
            saida_datetime = datetime.combine(self.data, self.saida)
            delta = saida_datetime - entrada_datetime

        if delta:
            return {"status": "Ponto Fechado", "horas_trabalhadas": delta}
        else:
            horas_corridas = datetime.now() - entrada_datetime
            return {"status": "Ponto Aberto", "horas_corridas": horas_corridas}

    def __str__(self):
        return f"Ponto de {self.funcionario.nome} - {self.data}"
