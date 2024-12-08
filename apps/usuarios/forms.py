# usuarios/forms.py
from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm

class UsuarioCreationForm(forms.ModelForm):
    """
    Formulario personalizado para crear un nuevo usuario.
    """
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, max_length=30)

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'genero', 'nacimiento']  # Campos del formulario

    def save(self, commit=True):
        # Guardar el objeto Usuario
        usuario = super().save(commit=False)
        if commit:
            usuario.set_password(self.cleaned_data["password"])  # Encriptar la contraseña
            usuario.save()
        return usuario
