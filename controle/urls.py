from django.urls import path

from .views import (
    CriarEmpresaView,
    CriarFuncionárioView,
    FiltrarPontoView,
    ListarFuncionariosView,
    LoginView,
    MenuView,
    RedirectView,
    RegistrarPontoView,
)

urlpatterns = [
    path("", RedirectView.as_view(), name="redirect"),
    path("login/", LoginView.as_view(), name="login"),
    path("menu/", MenuView.as_view(), name="menu"),
    path("criar/empresa/", CriarEmpresaView.as_view(), name="criar-empresa"),
    path("funcionarios/", ListarFuncionariosView.as_view(), name="funcionarios"),
    path(
        "criar/funcionarios/",
        CriarFuncionárioView.as_view(),
        name="criar-funcionarios",
    ),
    path(
        "ponto/",
        RegistrarPontoView.as_view(),
        name="registrar-pontos",
    ),
    path(
        "funcionarios/pontos/",
        FiltrarPontoView.as_view(),
        name="filtrar-pontos",
    ),
]
