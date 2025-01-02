from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


class UsuarioAdmin(UserAdmin):
    """
    Configuração de exibição e gerenciamento do modelo Usuario no Django Admin.

    Atributos:
        model (Model): Define o modelo associado a este admin.
        list_display (tupla): Campos exibidos na lista de usuários.
        fieldsets (tupla): Define as seções e campos ao visualizar/editar um usuário.
        add_fieldsets (tupla): Define as seções e campos ao adicionar um novo usuário.
        search_fields (tupla): Campos utilizados para busca.
        ordering (tupla): Define a ordenação padrão na lista de usuários.
    """

    model = Usuario
    list_display = ("cpf", "funcionario", "is_superuser")
    fieldsets = (
        (None, {"fields": ("cpf",)}),
        ("Permissões", {"fields": ("is_superuser",)}),
        ("Funcionário", {"fields": ("funcionario",)}),
    )
    add_fieldsets = (
        (
            "Credenciais",
            {
                "classes": ("wide",),
                "fields": (
                    "cpf",
                    "password",
                ),
            },
        ),
        (
            "Funcionário",
            {
                "classes": ("wide",),
                "fields": ("funcionario",),
            },
        ),
        (
            "Permissões",
            {
                "classes": ("wide",),
                "fields": ("is_superuser",),
            },
        ),
    )
    search_fields = ("cpf",)
    ordering = ("cpf",)


admin.site.register(Usuario, UsuarioAdmin)
