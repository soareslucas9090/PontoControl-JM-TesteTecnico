from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import EmpresaForm, FuncionarioForm, LoginForm
from .models import Empresa, Funcionario, Usuario


@method_decorator(csrf_protect, name="dispatch")
class LoginView(View):
    def get(self, request):
        form = LoginForm()

        return render(
            request=request,
            template_name="auth/login.html",
            context={"form": form},
        )

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            cpf = form.cleaned_data["cpf"]
            password = form.cleaned_data["password"]

            user = authenticate(cpf=cpf, password=password)

            if user == None:
                form.errors.clear()
                form.add_error(
                    None,
                    "Usuário e/ou senha incorreto(s)!",
                )
            else:
                login(request, user)

                return redirect(reverse("menu"))

            return render(
                request=request,
                template_name="auth/login.html",
                context={"form": form},
            )

        else:
            return render(
                request=request,
                template_name="auth/login.html",
                context={"form": form},
            )


@method_decorator(csrf_protect, name="dispatch")
class MenuView(LoginRequiredMixin, UserPassesTestMixin, View):
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    def get(self, request):
        empresas = Empresa.objects.all()

        return render(
            request=request,
            template_name="business/menu.html",
            context={
                "empresas": empresas,
            },
        )


@method_decorator(csrf_protect, name="dispatch")
class CriarEmpresaView(LoginRequiredMixin, UserPassesTestMixin, View):
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    def get(self, request):
        form = EmpresaForm()

        return render(
            request=request,
            template_name="business/create/empresas.html",
            context={"form": form},
        )

    def post(self, request):
        form = EmpresaForm(request.POST)

        if form.is_valid():
            nome = form.cleaned_data["nome"]
            endereco = form.cleaned_data["endereco"]

            try:
                Empresa.objects.create(nome=nome, endereco=endereco)

                return redirect("/menu/")
            except Exception as e:
                form.errors.clear()
                form.add_error(
                    None,
                    e,
                )

                return render(
                    request=request,
                    template_name="business/create/empresas.html",
                    context={"form": form},
                )

        else:
            return render(
                request=request,
                template_name="business/create/empresas.html",
                context={"form": form},
            )


class ListarFuncionáriosView(LoginRequiredMixin, UserPassesTestMixin, View):
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    def get(self, request):
        empresa_id = request.GET.get("empresa", None)

        if not empresa_id:
            messages.error(
                request,
                "É preciso acessar esta página a partir do menu, selecionando uma empresa!",
            )
            return redirect(reverse("menu"))
        else:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
            except Empresa.DoesNotExist:
                messages.error(request, "Empresa não encontrada!")
                return redirect(reverse("menu"))

        usuarios = Usuario.objects.filter(funcionario__empresa=empresa)

        return render(
            request=request,
            template_name="business/list/funcionarios.html",
            context={"usuarios": usuarios, "empresa": empresa},
        )


class CriarFuncionárioView(LoginRequiredMixin, UserPassesTestMixin, View):
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    def get(self, request):
        form = FuncionarioForm()

        empresa_id = request.GET.get("empresa", None)

        if not empresa_id:
            messages.error(
                request,
                "É preciso acessar esta página a partir do menu, selecionando uma empresa!",
            )
            return redirect(reverse("menu"))
        else:
            try:
                empresa = Empresa.objects.get(pk=empresa_id)
            except Empresa.DoesNotExist:
                messages.error(request, "Empresa não encontrada!")
                return redirect(reverse("menu"))

        return render(
            request=request,
            template_name="business/create/funcionarios.html",
            context={"empresa": empresa, "form": form},
        )

    def post(self, request):
        form = FuncionarioForm(request.POST)

        empresa_id = request.GET.get("empresa", None)
        empresa = Empresa.objects.get(pk=empresa_id)

        if form.is_valid():
            nome = form.cleaned_data["nome"]
            cpf = form.cleaned_data["cpf"]
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["senha"]

            funcionario = Funcionario.objects.create(
                nome=nome,
                email=email,
                empresa=empresa,
            )

            usuario = funcionario.criar_usuario(cpf, senha)

            messages.success(
                request,
                f"Funcionário de CPF {usuario.cpf} criado com sucesso!",
            )

            return redirect(reverse("funcionarios") + "?empresa=" + empresa_id)

        else:
            return render(
                request=request,
                template_name="business/create/funcionarios.html",
                context={"empresa": empresa, "form": form},
            )
