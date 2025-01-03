from django.urls import path

from .views import (
    CriarEmpresaView,
    CriarFuncionárioView,
    EditarEmpresaView,
    FiltrarPontoADMView,
    FiltrarPontoComumView,
    ListarFuncionariosView,
    LoginView,
    LogoutView,
    MenuView,
    RedirectView,
    RegistrarPontoView,
)

urlpatterns = [
    path("", RedirectView.as_view(), name="redirect"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("menu/", MenuView.as_view(), name="menu"),
    path("criar/empresa/", CriarEmpresaView.as_view(), name="criar-empresa"),
    path(
        "editar/empresa/<int:pk>/", EditarEmpresaView.as_view(), name="editar-empresa"
    ),
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
        FiltrarPontoADMView.as_view(),
        name="filtrar-pontos",
    ),
    path(
        "pontos/",
        FiltrarPontoComumView.as_view(),
        name="filtrar-pontos-comum",
    ),
]
