from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from .forms import RegistroNegocioForm
from .models import Negocio

class RegistrarNegocioView(CreateView):
    """
    Vista para registrar un nuevo negocio utilizando CreateView.
    """
    model = Negocio
    form_class = RegistroNegocioForm
    template_name = 'negocios/registrar_negocio.html'
    success_url = reverse_lazy('apps.negocios:iniciar_sesion')  # Redirigir a la página de iniciar sesión tras el registro

    def form_valid(self, form):
        """
        Si el formulario es válido, se guarda la contraseña de forma segura
        y luego se loguea al negocio automáticamente.
        """
        # Guardar el objeto negocio sin commit
        negocio = form.save(commit=False)
        # Establecer la contraseña de forma segura
        negocio.set_password(form.cleaned_data['password1'])
        negocio.save()
        return super().form_valid(form)

class ReportesView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar los reportes del negocio registrado.
    Requiere que el negocio esté logueado para acceder.
    """
    template_name = 'negocios/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['negocio'] = self.request.user  # Se obtiene el negocio logueado
        return context

class PerfilView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar el perfil del negocio registrado.
    """
    template_name = 'negocios/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['negocio'] = self.request.user  # Se obtiene el negocio logueado
        return context