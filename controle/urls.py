from django.urls import path

from .views import LoginView, MenuView, CriarEmpresaView, ListarFuncionáriosView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("menu/", MenuView.as_view(), name="menu"),
    path("criar/empresa/", CriarEmpresaView.as_view(), name="criar-empresa"),
    path("funcionarios/", ListarFuncionáriosView.as_view(), name="funcionarios"),
]
