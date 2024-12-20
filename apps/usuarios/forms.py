from django import forms
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class CommonUserRegistrationForm(forms.ModelForm):
    """Formulario de registro para usuarios comunes"""
    
    password = forms.CharField(widget=forms.PasswordInput)  # Campo para la contraseña
    genero_choices = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    genero = forms.ChoiceField(choices=genero_choices)  # Campo para género
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # Campo para fecha de nacimiento
    correo = forms.EmailField(max_length=60)  # Campo para el correo

    class Meta:
        model = CustomUser
        fields = ['username', 'correo', 'password', 'genero', 'fecha_nacimiento']  # Campos a mostrar en el formulario

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

        # Asigna los puntos iniciales solo si el usuario es de tipo 'common' y si no tiene puntos
        if user.is_common_user() and user.puntos is None:
            user.puntos = 5  # Asigna los puntos iniciales a 5 solo si aún no están asignados

        if commit:
            user.save()  # Guarda el usuario en la base de datos

        return user


# ------------------------------------------------------------------------------------------------------

class BusinessUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    # Opcional: Definir el campo username como obligatorio o con alguna lógica para generarlo automáticamente
    username = forms.CharField(max_length=30, required=True)  # Campo de username obligatorio

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'correo', 'password', 'provincia', 'ciudad', 'nombre_negocio']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Encripta la contraseña
        user.set_password(self.cleaned_data['password'])

        # Asigna el tipo de usuario como 'business'
        user.user_type = 'business'

        # Asigna los demás campos (de negocio) según lo ingresado en el formulario
        user.username = self.cleaned_data['username']  # Asigna el nombre de usuario
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.correo = self.cleaned_data['correo']
        user.provincia = self.cleaned_data['provincia']
        user.ciudad = self.cleaned_data['ciudad']
        user.nombre_negocio = self.cleaned_data['nombre_negocio']

        if commit:
            user.save()  # Guarda el usuario en la base de datos

        return user

# ------------------------------------------------------------------------------------------------------

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')

    class Meta:
        model = User
        fields = ['username', 'password']