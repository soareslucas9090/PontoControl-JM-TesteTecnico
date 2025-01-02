from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.utils import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import EmpresaForm, FiltroPontoForm, FuncionarioForm, LoginForm, PontoForm
from .models import Empresa, Funcionario, Ponto, Usuario


class ViewProtegida(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")


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
class MenuView(ViewProtegida, View):
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
class CriarEmpresaView(ViewProtegida, View):
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


class ListarFuncionariosView(ViewProtegida, View):
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
                request.session["empresa_id"] = empresa_id
            except Empresa.DoesNotExist:
                messages.error(request, "Empresa não encontrada!")
                return redirect(reverse("menu"))

        usuarios = Usuario.objects.filter(funcionario__empresa=empresa)

        return render(
            request=request,
            template_name="business/list/funcionarios.html",
            context={"usuarios": usuarios, "empresa": empresa},
        )


class CriarFuncionárioView(ViewProtegida, View):
    def get(self, request):
        form = FuncionarioForm()

        empresa_id = request.session.get("empresa_id", None)

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

        empresa_id = request.session.get("empresa_id", None)
        empresa = Empresa.objects.get(pk=empresa_id)

        if form.is_valid():
            nome = form.cleaned_data["nome"]
            cpf = form.cleaned_data["cpf"]
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["senha"]

            try:
                Funcionario.objects.get(email=email)

                form.errors.clear()
                form.add_error(
                    "email",
                    "Já há um email registrado com este nome e domínio.",
                )

                return render(
                    request=request,
                    template_name="business/create/funcionarios.html",
                    context={"empresa": empresa, "form": form},
                )
            except Funcionario.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(cpf=cpf)

                    form.errors.clear()
                    form.add_error(
                        "cpf",
                        f"Já existe um funcionário registrado com este CPF na empresa {usuario.funcionario.empresa}",
                    )

                    return render(
                        request=request,
                        template_name="business/create/funcionarios.html",
                        context={"empresa": empresa, "form": form},
                    )

                except:
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


class RegistrarPontoView(ViewProtegida, View):
    def get(self, request):
        form = PontoForm()

        empresa_id = request.session.get("empresa_id", None)

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
            template_name="business/main/registro_ponto.html",
            context={"empresa": empresa, "form": form},
        )

    def post(self, request):
        form = PontoForm(request.POST)

        empresa_id = request.session.get("empresa_id", None)
        empresa = Empresa.objects.get(pk=empresa_id)

        if form.is_valid():
            cpf = form.cleaned_data["CPF"]

            funcionario = Usuario.objects.filter(cpf=cpf, funcionario__empresa=empresa)

            if funcionario:
                funcionario = funcionario.first().funcionario

                try:
                    ponto_existente = Ponto.objects.get(
                        funcionario=funcionario, saida=None
                    )

                    ponto_existente.saida = now().time()

                    ponto_existente.save()

                    horas = ponto_existente.horas_trabalhadas()["horas_trabalhadas"]

                    return render(
                        request=request,
                        template_name="business/main/registro_ponto.html",
                        context={
                            "empresa": empresa,
                            "form": form,
                            "status": "Ponto Fechado",
                            "horas_trabalhadas": horas,
                        },
                    )
                except Ponto.DoesNotExist:
                    Ponto.objects.create(funcionario=funcionario)
                    form.errors.clear()

                    return render(
                        request=request,
                        template_name="business/main/registro_ponto.html",
                        context={
                            "empresa": empresa,
                            "form": form,
                            "status": "Ponto Aberto",
                        },
                    )
            else:
                form.errors.clear()
                form.add_error(
                    "CPF",
                    "Funcionário não encontrado, tente novamente.",
                )

                return render(
                    request=request,
                    template_name="business/main/registro_ponto.html",
                    context={"empresa": empresa, "form": form},
                )

        else:
            return render(
                request=request,
                template_name="business/main/registro_ponto.html",
                context={"empresa": empresa, "form": form},
            )


class FiltrarPontoView(ViewProtegida, View):
    def get(self, request):
        form = FiltroPontoForm()

        funcionario_id = request.GET.get("funcionario", None)

        if not funcionario_id:
            messages.error(
                request,
                "Selecione uma empresa e depois um funcionário!",
            )
            return redirect(reverse("menu"))
        else:
            try:
                funcionario = Funcionario.objects.get(pk=funcionario_id)

                if funcionario.empresa.id != int(request.session.get("empresa_id")):
                    messages.error(
                        request,
                        "Funcionário não pertence a empresa selecionada!",
                    )
                    return redirect(reverse("menu"))
            except Funcionario.DoesNotExist:
                messages.error(request, "Funcionário não encontrado!")
                return redirect(reverse("menu"))

        return render(
            request=request,
            template_name="business/main/listar_pontos.html",
            context={"funcionario": funcionario, "form": form, "filtrado": False},
        )

    def post(self, request):
        form = FiltroPontoForm(request.POST)

        funcionario_id = request.GET.get("funcionario", None)
        funcionario = Funcionario.objects.get(pk=funcionario_id)

        if form.is_valid():
            data_inicial = form.cleaned_data["data_inicial"]
            data_final = form.cleaned_data["data_final"]

            pontos = Ponto.objects.filter(
                data__range=(data_inicial, data_final)
            ).order_by("data")

            return render(
                request=request,
                template_name="business/main/listar_pontos.html",
                context={
                    "funcionario": funcionario,
                    "form": form,
                    "filtrado": True,
                    "pontos": pontos,
                },
            )

        else:
            return render(
                request=request,
                template_name="business/main/listar_pontos.html",
                context={"funcionario": funcionario, "form": form, "filtrado": False},
            )
