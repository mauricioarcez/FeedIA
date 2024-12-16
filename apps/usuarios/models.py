# apps/usuarios/models.py

import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
    
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('common', 'Usuario Común'),
        ('business', 'Usuario Negocio'),
    )
    
    # Tipo de usuario (común o negocio)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='common')

    # Puntos del usuario (opcional para los usuarios comunes). Comienza con 5 puntos.
    puntos = models.PositiveIntegerField(default=5, blank=True, null=True)  # Puntos pueden ser nulos, ya que es opcional para usuarios comunes

    # Correo electrónico (único para evitar duplicados)
    correo = models.EmailField(max_length=60, unique=True, blank=False)  # Correo obligatorio, no nulo

    # Campos de negocio
    first_name = models.CharField(max_length=30, blank=False)  # Nombre obligatorio, no nulo
    last_name = models.CharField(max_length=30, blank=False)  # Apellido obligatorio, no nulo
    nombre_negocio = models.CharField(max_length=60, blank=False)  # Nombre de negocio obligatorio, no nulo
    provincia = models.CharField(max_length=50, blank=False)  # Provincia obligatoria, no nula
    ciudad = models.CharField(max_length=60, blank=False)  # Ciudad obligatoria, no nula

    # Validación personalizada de correo
    def clean(self):
        super().clean()
        if self.correo:
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(pattern, self.correo):
                raise ValidationError('Formato de correo inválido.')

    def is_common_user(self):
        return self.user_type == 'common'

    def is_business_user(self):
        return self.user_type == 'business'
