from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.utils import IntegrityError
from django.http import HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import EmpresaForm, FiltroPontoForm, FuncionarioForm, LoginForm, PontoForm
from .models import Empresa, Funcionario, Ponto, Usuario


class ViewProtegida(LoginRequiredMixin, UserPassesTestMixin):
    """
    Classe base para proteger visualizações. Apenas usuários com acesso de SUPERUSER.

    Atributos:
        redirect_field_name (str): Nome do campo usado para redirecionamento após o login. É usado o
        valor padrão "next".

    Métodos:
        test_func(): Define a lógica para verificar se o usuário tem permissão.
        handle_no_permission(): Trata o caso de falta de permissão, redirecionando e exibindo uma mensagem.
    """

    redirect_field_name = "next"

    def test_func(self):
        """
        Verifica se o usuário atual é superusuário.

        Retorno:
            Booleano: Verdadeiro se o usuário for superusuário, caso contrário, Falso.
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Trata a falta de permissão redirecionando o usuário para a página de login com uma mensagem de erro.

        Retorno:
            HttpResponse: Redirecionamento para a página de login.
        """
        messages.error(
            self.request,
            "Você não tem permissão para acessar esta página.",
        )
        return redirect(reverse("login"))


@method_decorator(csrf_protect, name="dispatch")
class RedirectView(View):
    """
    Redireciona o usuário para diferentes páginas dependendo do tipo de usuário.

    Métodos:
        get(request): Lida com requisições GET para redirecionar o usuário.
    """

    def get(self, request):
        """
        Redireciona o usuário com base em seu status de autenticação e privilégios.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redirecionamento para a página apropriada.
        """
        if isinstance(request.user, AnonymousUser):
            return redirect(reverse("login"))

        if not request.user.is_superuser:
            return redirect(reverse("filtrar-pontos-comum"))

        return redirect(reverse("menu"))


@method_decorator(csrf_protect, name="dispatch")
class LoginView(View):
    """
    Gerencia o login de usuários.

    Métodos:
        get(request): Exibe o formulário de login.
        post(request): Lida com o envio do formulário de login e autenticação do usuário.
    """

    def get(self, request):
        """
        Renderiza a página de login com o formulário vazio.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de login renderizada.
        """
        form = LoginForm()

        return render(
            request=request,
            template_name="auth/login.html",
            context={"form": form},
        )

    def post(self, request):
        """
        Processa o formulário de login e autentica o usuário.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redireciona ou renderiza novamente a página de login com erros.
        """
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

                if user.funcionario:
                    request.session["funcionario_id"] = user.funcionario.id

                return redirect(reverse("redirect"))

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
    """
    Exibe o menu principal ao gestor.

    Métodos:
        get(request): Renderiza o menu.
    """

    def get(self, request):
        """
        Faz a query de empresas e renderiza o menu.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de menu renderizada.
        """
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
    """
    Página para criação de novas empresas.

    Métodos:
        get(request): Exibe o formulário de criação de empresas.
        post(request): Lida com o envio do formulário de criação de empresas e efetiva as alterações.
    """

    def get(self, request):
        """
        Renderiza a página de crição de empresa com o formulário vazio.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de login renderizada.
        """
        form = EmpresaForm()

        return render(
            request=request,
            template_name="business/create/empresas.html",
            context={"form": form},
        )

    def post(self, request):
        """
        Processa o formulário de criação de empresa e exibe mensagem de sucesso ao usuário.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redireciona ou renderiza novamente a página de criação de empresas com erros.
        """
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
    """
    Página para listagem de funcionários da empresa escolhida.

    Métodos:
        get(request): Renderiza a página de listagem de funcionários.
    """

    def get(self, request):
        """
        Exibe a página de listagem de funcionários da empresa escolhida.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Renderiza a página ou redireciona de volta ao menu exibindo uma mensagem de erro.
        """
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
    """
    Página para criação de funcionários da empresa escolhida.

    Métodos:
        get(request): Exibe o formulário de criação de funcionários.
        post(request): Lida com o envio do formulário de criação de funcionários e efetiva as alterações.
    """

    def get(self, request):
        """
        Renderiza a página de crição de funcionários com o formulário vazio.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de criação de funcionários renderizada ou redirecionamento de volta
            ao menu em caso de erros.
        """
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
        """
        Processa o formulário de criação de funcionários e exibe mensagem de sucesso ou erro ao usuário.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redireciona ou renderiza novamente a página de crição de funcionários com erro.
        """
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
    """
    Página para registro de ponto dos funcionários da empresa escolhida.

    Métodos:
        get(request): Exibe o formulário de registro de ponto de funcionários.
        post(request): Lida com o envio do formulário de registro de ponto dos funcionários e exibe o status
        do ponto ou erros gerados.
    """

    def get(self, request):
        """
        Renderiza a página de registro de ponto dos funcionários com o formulário vazio.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de registro de ponto dos funcionários renderizada ou redirecionamento de volta
            ao menu em caso de erros.
        """
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
        """
        Processa o formulário de egistro de ponto de funcionários e exibe mensagem de sucesso ou erro ao usuário.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redireciona ou renderiza novamente a página de registro de ponto de funcionários com erro.
        """
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


class FiltrarPontoADMView(ViewProtegida, View):
    """
    Página para filtragem e visualização dos pontos do funcionário escolhido na visão do gestor.

    Métodos:
        get(request): Exibe a página de listagem de pontos do funcionário escolhido.
        post(request): Lida com o filtro de datas aplicado e exibe os pontos filtrados.
    """

    def get(self, request):
        """
        Renderiza a página de listagem de pontos do funcionário escolhido.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de listagem dos pontos do funcionário renderizada ou redirecionamento de volta
            ao menu em caso de erros.
        """
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
        """
        Processa a filtragem de pontos do funcionário e lista os pontos filtrados.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: renderiza novamente a página com a listagem dos pontos fitrados ou em caso de erros
            renderiza novamente com os erros gerados ou redireciona para a página de login.
        """
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


class FiltrarPontoComumView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Página para filtragem e visualização dos pontos do funcionário logado.

    Atributos:
        redirect_field_name (str): Nome do campo usado para redirecionamento após o login. É usado o
        valor padrão "next".

    Métodos:
        test_func(): Define a lógica para verificar se o usuário tem permissão de acesso.
        handle_no_permission(): Trata o caso de falta de permissão, redirecionando e exibindo uma mensagem.
        get(request): Exibe a página de listagem de pontos do funcionário que fez login.
        post(request): Lida com o filtro de datas aplicado e exibe os pontos filtrados.
    """

    redirect_field_name = "next"

    def test_func(self):
        """
        Verifica se o usuário atual não é anônimo e não é superusuário.

        Retorno:
            Booleano: Verdadeiro se o usuário não for superusuário e nem anônimo, caso contrário em qualquer uma das
            duas hipóteses, Falso.
        """
        if isinstance(self.request.user, AnonymousUser):
            return False

        return not self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Você não tem permissão para acessar esta página.",
        )
        return redirect(reverse("login"))

    def get(self, request):
        """
        Renderiza a página de listagem de pontos do funcionário logado.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de listagem dos pontos do funcionário renderizada ou redirecionamento de volta
            ao login em caso de erros.
        """
        form = FiltroPontoForm()

        funcionario_id = request.session.get("funcionario_id", None)

        if not funcionario_id:
            messages.error(
                request,
                "Esta página é destinada apenas a funcionários",
            )
            return redirect(reverse("login"))
        else:
            try:
                funcionario = Funcionario.objects.get(pk=funcionario_id)
            except Funcionario.DoesNotExist:
                messages.error(request, "Funcionário não encontrado!")
                return redirect(reverse("login"))

        return render(
            request=request,
            template_name="business/main/listar_pontos.html",
            context={"funcionario": funcionario, "form": form, "filtrado": False},
        )

    def post(self, request):
        """
        Processa a filtragem de pontos do funcionário e lista os pontos filtrados.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: renderiza novamente a página com a listagem dos pontos fitrados ou em caso de erros
            renderiza novamente com os erros gerados ou redireciona para a página de login.
        """
        form = FiltroPontoForm(request.POST)

        funcionario_id = request.session.get("funcionario_id", None)

        if funcionario_id != request.user.funcionario.id:
            messages.error(
                request,
                "Erro na integridade dos dados da página!",
            )
            return redirect(reverse("login"))

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
