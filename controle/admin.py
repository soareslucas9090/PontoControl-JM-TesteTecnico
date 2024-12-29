from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


class UsuarioAdmin(UserAdmin):
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
            "Funcinário",
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
