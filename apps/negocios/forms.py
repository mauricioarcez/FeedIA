# apps/negocios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Negocio

class RegistroNegocioForm(UserCreationForm):
    """
    Formulario para registrar un negocio. Este formulario usará el modelo Negocio.
    """
    class Meta:
        model = Negocio
        fields = ['nombre_negocio', 'provincia', 'categoria_negocio', 'direccion', 'correo_dueño', 'telefono']
        widgets = {
            'nombre_negocio': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria_negocio': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_dueño': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña',
        help_text="Contraseña de al menos 8 caracteres.",
        min_length=8
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña',
        help_text="Debe coincidir con la contraseña anterior.",
    )
