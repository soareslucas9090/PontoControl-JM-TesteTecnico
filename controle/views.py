from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import LoginForm, EmpresaForm
from .models import Empresa, Funcionario
from django.http import HttpResponseForbidden


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

        funcionarios = Funcionario.objects.filter(empresa=empresa)

        return render(
            request=request,
            template_name="business/list/funcionarios.html",
            context={"funcionarios": funcionarios, "empresa": empresa.nome},
        )
