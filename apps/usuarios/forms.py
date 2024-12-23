from django import forms
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime


class CommonUserRegistrationForm(forms.ModelForm):
    """Formulario de registro para usuarios comunes"""
    
    password = forms.CharField(widget=forms.PasswordInput)  # Campo para la contraseña
    genero = forms.ChoiceField(
        choices=CustomUser.GENERO_CHOICES,
        required=True,  # Obligatorio para usuarios comunes
        error_messages={'required': 'Por favor selecciona tu género'}
    )
    
    fecha_nacimiento = forms.DateField(
        required=True,  # Obligatorio para usuarios comunes
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        error_messages={'required': 'Por favor ingresa tu fecha de nacimiento'}
    )
    
    correo = forms.EmailField(max_length=60)  # Campo para el correo
    
    # Nuevos campos para ubicación
    ciudad = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Resistencia',
            'class': 'form-control'
        })
    )
    provincia = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Chaco',
            'class': 'form-control'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'correo', 
            'password', 
            'genero', 
            'fecha_nacimiento',
            'ciudad',
            'provincia'
        ]

    def save(self, commit=True):
        """Guarda el usuario, asigna puntos y encripta la contraseña"""
        user = super().save(commit=False)  # No guardamos todavía el usuario

        # Encripta la contraseña
        user.set_password(self.cleaned_data['password'])

        # Asigna el tipo de usuario
        user.user_type = 'common'  # Asigna 'common' como tipo de usuario por defecto
        user.genero = self.cleaned_data['genero']  # Asigna el género
        user.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']  # Asigna la fecha de nacimiento
        user.correo = self.cleaned_data['correo']  # Asigna el correo
        user.ciudad = self.cleaned_data['ciudad'].lower().capitalize()  # Normaliza la ciudad
        user.provincia = self.cleaned_data['provincia'].lower().capitalize()  # Normaliza la provincia

        # Asigna los puntos iniciales solo si el usuario es de tipo 'common' y si no tiene puntos
        if user.is_common_user() and user.puntos is None:
            user.puntos = 5  # Asigna los puntos iniciales a 5 solo si aún no están asignados

        if commit:
            user.save()  # Guarda el usuario en la base de datos

        return user

    def clean(self):
        cleaned_data = super().clean()
        # Validaciones específicas para campos obligatorios
        if not cleaned_data.get('genero'):
            self.add_error('genero', 'Este campo es obligatorio')
        if not cleaned_data.get('fecha_nacimiento'):
            self.add_error('fecha_nacimiento', 'Este campo es obligatorio')
        return cleaned_data

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            # Validar que la fecha no sea futura
            if fecha > datetime.now().date():
                raise forms.ValidationError('La fecha no puede ser futura')
            
            # Validar edad mínima
            edad = (datetime.now().date() - fecha).days / 365
            if edad < 13:
                raise forms.ValidationError('Debes tener al menos 13 años para registrarte')
        
        return fecha


# ------------------------------------------------------------------------------------------------------

class BusinessUserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'correo', 'password', 'provincia', 'ciudad', 
                 'nombre_negocio', 'first_name', 'last_name']
        # No incluimos género ni fecha_nacimiento

# ------------------------------------------------------------------------------------------------------

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')

    class Meta:
        model = User
        fields = ['username', 'password']