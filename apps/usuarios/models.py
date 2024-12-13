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
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='common')
    puntos = models.PositiveIntegerField(default=5, blank=True, null=True)  # Comienza con 5 puntos
    
    # negocios datos
    correo = models.EmailField(max_length=255, blank=True, null=True, unique=True)  
    first_name = models.CharField(max_length=255)  
    last_name = models.CharField(max_length=255, blank=True, null=True) 
    nombre_negocio = models.CharField(max_length=255, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

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
