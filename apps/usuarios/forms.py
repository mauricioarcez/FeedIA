from django import forms
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime


class CommonUserRegistrationForm(forms.ModelForm):
    """Formulario de registro para usuarios comunes"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'correo', 'password', 'provincia', 'ciudad', 'genero', 'fecha_nacimiento']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        """Guarda el usuario, asigna puntos y encripta la contraseña"""
        user = super().save(commit=False)  # No guardamos todavía el usuario

        # Encripta la contraseña
        user.set_password(self.cleaned_data['password'])

        # Asigna el tipo de usuario
        user.user_type = 'common'  # Asigna 'common' como tipo de usuario por defecto

        # Normaliza la ciudad y provincia
        user.ciudad = self.cleaned_data['ciudad'].lower().capitalize()
        user.provincia = self.cleaned_data['provincia'].lower().capitalize()

        if commit:
            user.save()  # Guarda el usuario en la base de datos

        return user

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')  # Asegúrate de obtener el tipo de usuario

        # Validaciones específicas para usuarios comunes
        if user_type == 'common':
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
    """Formulario de registro para usuarios de negocio"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'correo', 'password', 'provincia', 'ciudad', 
                  'nombre_negocio', 'first_name', 'last_name']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'nombre_negocio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del negocio'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mensajes de ayuda
        self.fields['username'].help_text = 'Elige un nombre de usuario único.'
        self.fields['correo'].help_text = 'Introduce un correo electrónico válido.'
        self.fields['password'].help_text = 'La contraseña debe tener al menos 8 caracteres.'
        self.fields['provincia'].help_text = 'Selecciona tu provincia.'
        self.fields['ciudad'].help_text = 'Introduce la ciudad donde se encuentra tu negocio.'
        self.fields['nombre_negocio'].help_text = 'Nombre de tu negocio.'

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if CustomUser.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya está en uso. Por favor, elige otro.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        # Validaciones adicionales si es necesario
        if not cleaned_data.get('provincia'):
            self.add_error('provincia', 'Este campo es obligatorio.')
        if not cleaned_data.get('ciudad'):
            self.add_error('ciudad', 'Este campo es obligatorio.')
        if not cleaned_data.get('nombre_negocio'):
            self.add_error('nombre_negocio', 'Este campo es obligatorio.')
        if not cleaned_data.get('first_name'):
            self.add_error('first_name', 'Este campo es obligatorio.')
        if not cleaned_data.get('last_name'):
            self.add_error('last_name', 'Este campo es obligatorio.')

        return cleaned_data

    def save(self, commit=True):
        """Guarda el usuario, asigna puntos y encripta la contraseña"""
        user = super().save(commit=False)  # No guardamos todavía el usuario

        # Encripta la contraseña
        user.set_password(self.cleaned_data['password'])

        # Asigna el tipo de usuario
        user.user_type = 'business'  # Asigna 'business' como tipo de usuario por defecto

        # Normaliza la ciudad y provincia
        user.ciudad = self.cleaned_data['ciudad'].lower().capitalize()
        user.provincia = self.cleaned_data['provincia'].lower().capitalize()

        if commit:
            user.save()  # Guarda el usuario en la base de datos

        return user

# ------------------------------------------------------------------------------------------------------

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')

    class Meta:
        model = User
        fields = ['username', 'password']