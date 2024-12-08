# usuarios/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import UsuarioCreationForm
from .models import Usuario

class RegistroUsuarioView(CreateView):
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('apps.usuarios:usuario_login')  # Redirige después del registro

    def form_valid(self, form):
        # Guardar el usuario
        usuario = form.save()
        # Iniciar sesión automáticamente después de registrarse
        login(self.request, usuario)
        return super().form_valid(form)
