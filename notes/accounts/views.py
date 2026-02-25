from django.shortcuts import redirect, render
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from .forms import RegisterForm, LoginForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.decorators import login_required
from utils.forms import style_form
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

User = get_user_model()

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Cuenta creada correctamente. ¡Bienvenido!')
        return super().form_valid(form)
    
class LoginView(FormView):  
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def get_form_kargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        next_url = self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return super().form_valid(form.__class__(data=None)) or self.redirect(next_url)
        return super().form_valid(form)
    
    def redirect(self, url):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(url)
    
@login_required
def home_view(request):
    if request.method == "POST":
        # Ejemplo: procesar un campo de texto del formulario
        mensaje = request.POST.get("mensaje")
        if mensaje:
            messages.success(request, f"Has enviado: {mensaje}")
            return redirect("home")  # Evita reenvíos de formulario al recargar
        else:
            messages.error(request, "Por favor, escribe algo antes de enviar.")

    return render(request, "accounts/home.html")

class MyPasswordResetView(PasswordResetView):
    # mismos template_name que ya usas
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        style_form(form)
        return form

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        style_form(form)
        return form
