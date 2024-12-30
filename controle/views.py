from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import LoginForm


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
                print("não autenticado")
            else:
                print("autenticado")
                print(request.user)
                login(request, user)
                print(request.user)

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
