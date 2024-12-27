# Generated by Django 5.1.4 on 2024-12-27 20:16

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('endereco', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='funcionarios', to='controle.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Ponto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('entrada', models.TimeField()),
                ('saida', models.TimeField(null=True)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pontos', to='controle.funcionario')),
            ],
        ),
    ]
