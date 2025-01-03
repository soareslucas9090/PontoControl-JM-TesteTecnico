from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
import fitz
from datetime import datetime
from django.views.decorators.csrf import csrf_protect

from .forms import EmpresaForm, FiltroPontoForm, FuncionarioForm, LoginForm, PontoForm
from .models import Empresa, Endereco, Funcionario, Ponto, Usuario


class ViewProtegidaADM(LoginRequiredMixin, UserPassesTestMixin):
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


class ViewProtegidaComum(LoginRequiredMixin, UserPassesTestMixin):
    """
    Classe base para proteger visualizações. Apenas usuários não anônimos e não superusuários.

    Atributos:
        redirect_field_name (str): Nome do campo usado para redirecionamento após o login. É usado o
        valor padrão "next".

    Métodos:
        test_func(): Define a lógica para verificar se o usuário tem permissão de acesso.
        handle_no_permission(): Trata o caso de falta de permissão, redirecionando e exibindo uma mensagem.
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
class LogoutView(View):
    """
    Faz o Logout do usuário.

    Métodos:
        get(request): Faz o logout do usuário e redireciona para a página de login.
    """

    def get(self, request):
        """
        Faz o logout do usuário e redireciona para a página de login.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Redirecionamento para a página de login.
        """
        logout(request)

        return redirect(reverse("login"))


@method_decorator(csrf_protect, name="dispatch")
class MenuView(ViewProtegidaADM, View):
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
class CriarEmpresaView(ViewProtegidaADM, View):
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
            logradouro = form.cleaned_data["logradouro"]
            numero = form.cleaned_data["numero"]
            complemento = form.cleaned_data["complemento"]
            bairro = form.cleaned_data["bairro"]
            cidade = form.cleaned_data["cidade"]
            estado = form.cleaned_data["estado"]
            cep = form.cleaned_data["cep"]

            endereco = Endereco.objects.create(
                logradouro=logradouro,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                cep=cep,
            )

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


@method_decorator(csrf_protect, name="dispatch")
class EditarEmpresaView(ViewProtegidaADM, View):
    """
    Página para edição de empresas existentes.

    Métodos:
        get(request, pk): Exibe o formulário preenchido com os dados da empresa.
        post(request, pk): Lida com o envio do formulário de edição e atualiza os dados.
    """

    def get(self, request, pk):
        """
        Renderiza a página de edição de empresa com os dados existentes.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.
            pk (int): O ID da empresa a ser editada.

        Retorno:
            HttpResponse: Página de edição de empresa renderizada.
        """
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            messages.error(
                request,
                "É preciso acessar esta página a partir do menu, selecionando uma empresa!",
            )
            return redirect(reverse("menu"))
        endereco = empresa.endereco

        form = EmpresaForm(
            initial={
                "nome": empresa.nome,
                "logradouro": endereco.logradouro,
                "numero": endereco.numero,
                "complemento": endereco.complemento,
                "bairro": endereco.bairro,
                "cidade": endereco.cidade,
                "estado": endereco.estado,
                "cep": endereco.cep,
            }
        )

        return render(
            request=request,
            template_name="business/create/empresas.html",
            context={"form": form, "is_editing": True, "empresa_id": pk},
        )

    def post(self, request, pk):
        """
        Processa o formulário de edição e salva as alterações.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.
            pk (int): O ID da empresa a ser editada.

        Retorno:
            HttpResponse: Redireciona ou renderiza novamente a página com erros.
        """
        empresa = Empresa.objects.get(pk=pk)
        endereco = empresa.endereco

        form = EmpresaForm(request.POST)

        if form.is_valid():
            endereco.logradouro = form.cleaned_data["logradouro"]
            endereco.numero = form.cleaned_data["numero"]
            endereco.complemento = form.cleaned_data["complemento"]
            endereco.bairro = form.cleaned_data["bairro"]
            endereco.cidade = form.cleaned_data["cidade"]
            endereco.estado = form.cleaned_data["estado"]
            endereco.cep = form.cleaned_data["cep"]
            endereco.save()

            empresa.nome = form.cleaned_data["nome"]
            empresa.endereco = endereco
            empresa.save()

            messages.success(
                request,
                "Alterações realizadas com sucesso!",
            )

            return redirect("/menu/")
        else:
            return render(
                request=request,
                template_name="business/create/empresas.html",
                context={"form": form, "is_editing": True, "empresa_id": pk},
            )


@method_decorator(csrf_protect, name="dispatch")
class ListarFuncionariosView(ViewProtegidaADM, View):
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


@method_decorator(csrf_protect, name="dispatch")
class CriarFuncionarioView(ViewProtegidaADM, View):
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


@method_decorator(csrf_protect, name="dispatch")
class EditarFuncionarioView(ViewProtegidaADM, View):
    """
    Página para criação de funcionários da empresa escolhida.

    Métodos:
        get(request): Exibe o formulário de criação de funcionários.
        post(request): Lida com o envio do formulário de criação de funcionários e efetiva as alterações.
    """

    def get(self, request, pk):
        """
        Renderiza a página de crição de funcionários com o formulário vazio.

        Parâmetros:
            request (HttpRequest): O objeto da requisição HTTP.

        Retorno:
            HttpResponse: Página de criação de funcionários renderizada ou redirecionamento de volta
            ao menu em caso de erros.
        """
        try:
            funcionario = Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            messages.error(
                request,
                "É preciso acessar esta página a partir do menu, selecionando uma empresa e depois um funcionário!",
            )
            return redirect(reverse("menu"))

        form = FuncionarioForm(
            initial={
                "nome": funcionario.nome,
                "cpf": funcionario.usuarios.all().first().cpf,
                "email": funcionario.email,
                "senha": funcionario.usuarios.all().first().password,
            }
        )

        empresa_id = request.session.get("empresa_id", None)

        if not empresa_id:
            messages.error(
                request,
                "É preciso acessar esta página a partir do menu, selecionando uma empresa e depois um funcionário!",
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
            context={
                "empresa": empresa,
                "is_editing": True,
                "funcionario_id": pk,
                "form": form,
            },
        )

    def post(self, request, pk):
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
        funcionario = Funcionario.objects.get(pk=pk)

        if form.is_valid():
            nome = form.cleaned_data["nome"]
            cpf = form.cleaned_data["cpf"]
            email = form.cleaned_data["email"]
            senha = form.cleaned_data["senha"]

            try:
                Funcionario.objects.exclude(pk=pk).get(email=email)

                form.errors.clear()
                form.add_error(
                    "email",
                    "Já há um email registrado com este nome e domínio.",
                )

                return render(
                    request=request,
                    template_name="business/create/funcionarios.html",
                    context={
                        "empresa": empresa,
                        "is_editing": True,
                        "funcionario_id": pk,
                        "form": form,
                    },
                )
            except Funcionario.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(funcionario=funcionario)
                    Usuario.objects.exclude(pk=usuario.pk).get(cpf=cpf)

                    form.errors.clear()
                    form.add_error(
                        "cpf",
                        f"Já existe um funcionário registrado com este CPF na empresa {usuario.funcionario.empresa}",
                    )

                    return render(
                        request=request,
                        template_name="business/create/funcionarios.html",
                        context={
                            "empresa": empresa,
                            "is_editing": True,
                            "funcionario_id": pk,
                            "form": form,
                        },
                    )

                except:
                    funcionario.nome = nome
                    funcionario.email = email
                    funcionario.save()

                    usuario = Usuario.objects.get(funcionario=funcionario)
                    usuario.cpf = cpf

                    if senha != usuario.password:
                        password = make_password(senha)
                        usuario.password = password

                    usuario.save()

            messages.success(
                request,
                f"Funcionário atualizado com sucesso!",
            )

            return redirect(reverse("funcionarios") + "?empresa=" + empresa_id)

        else:
            return render(
                request=request,
                template_name="business/create/funcionarios.html",
                context={
                    "empresa": empresa,
                    "is_editing": True,
                    "funcionario_id": pk,
                    "is_editing": True,
                    "form": form,
                },
            )


@method_decorator(csrf_protect, name="dispatch")
class RegistrarPontoView(ViewProtegidaADM, View):
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


def exportar_pdf(pontos, funcionario):
    pdf_document = fitz.open()
    page = pdf_document.new_page()

    header = f"Relatório de Pontos - {funcionario.nome}\n"
    sub_header = f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
    text = header + sub_header

    for ponto in pontos:
        text += f"Data: {ponto.data.strftime('%d/%m/%Y')} - Horas Trabalhadas: {ponto.horas_trabalhadas()['horas_trabalhadas']}\n"

    page.insert_textbox(
        fitz.Rect(72, 72, 500, 800),
        text,
        fontsize=12,
        fontname="helv",
        align=0,
    )

    pdf_bytes = pdf_document.write()
    pdf_document.close()

    return pdf_bytes


@method_decorator(csrf_protect, name="dispatch")
class FiltrarPontoADMView(ViewProtegidaADM, View):
    """
    Página para filtragem e visualização dos pontos do funcionário escolhido na visão do gestor.

    Métodos:
        get(request): Exibe a página de listagem de pontos do funcionário escolhido.
        post(request): Lida com o filtro de datas aplicado e exibe ou faz o download dos pontos filtrados.
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
            HttpResponse: renderiza novamente a página com a listagem dos pontos fitrados ou faz o download do
            PDF exportado ou, em caso de erros, renderiza novamente com os erros gerados ou redireciona para a página de login.
        """
        form = FiltroPontoForm(request.POST)

        funcionario_id = request.GET.get("funcionario", None)
        funcionario = Funcionario.objects.get(pk=funcionario_id)

        if form.is_valid():
            data_inicial = form.cleaned_data["data_inicial"]
            data_final = form.cleaned_data["data_final"]

            pontos = Ponto.objects.filter(
                data__range=(data_inicial, data_final), funcionario=funcionario
            ).order_by("data")

            form_export = request.POST.get("form-export")

            if form_export == "pdf":
                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = (
                    f"attachment; filename=relatorio_pontos_{funcionario.nome}.pdf"
                )
                pdf_bytes = exportar_pdf(pontos, funcionario)
                response.write(pdf_bytes)

                return response

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


@method_decorator(csrf_protect, name="dispatch")
class FiltrarPontoComumView(ViewProtegidaComum, View):
    """
    Página para filtragem e visualização dos pontos do funcionário logado.

    Métodos:
        get(request): Exibe a página de listagem de pontos do funcionário que fez login.
        post(request): Lida com o filtro de datas aplicado e exibe ou faz o dowload dos pontos filtrados.
    """

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
            HttpResponse: renderiza novamente a página com a listagem dos pontos fitradosfaz o download do
            PDF exportado ou, em caso de erros, renderiza novamente com os erros gerados ou redireciona para a página de login.
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
                data__range=(data_inicial, data_final), funcionario=funcionario
            ).order_by("data")

            form_export = request.POST.get("form-export")

            if form_export == "pdf":
                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = (
                    f"attachment; filename=relatorio_pontos_{funcionario.nome}.pdf"
                )
                pdf_bytes = exportar_pdf(pontos, funcionario)
                response.write(pdf_bytes)

                return response

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
