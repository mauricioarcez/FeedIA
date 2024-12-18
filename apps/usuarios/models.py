# apps/usuarios/models.py
import random
import string
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone
    
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

    codigo_encuesta = models.CharField(max_length=4, blank=True, null=True)
    fecha_expiracion_codigo = models.DateTimeField(null=True, blank=True)
    codigo_usado = models.BooleanField(default=False)  # Nuevo campo para verificar si el código ya fue usado

    def generar_codigo_encuesta(self):
        """Genera un código único de 4 dígitos para la encuesta, comprobando que no exista"""
        while True:
            codigo = ''.join(random.choices(string.digits, k=4))
            if not CustomUser.objects.filter(codigo_encuesta=codigo).exists():
                self.codigo_encuesta = codigo
                self.fecha_expiracion_codigo = timezone.now() + timedelta(hours=24)  # Expira en 24 horas
                self.codigo_usado = False  # Asegura que el código no ha sido usado
                self.save()
                break

    def codigo_expirado(self):
        """Verifica si el código de la encuesta ha expirado"""
        if self.codigo_usado:
            return True  # El código ya fue utilizado
        if self.fecha_expiracion_codigo and timezone.now() > self.fecha_expiracion_codigo:
            return True  # El código ha expirado
        return False

    def marcar_codigo_como_usado(self):
        """Marca el código como usado para evitar múltiples respuestas"""
        self.codigo_usado = True
        self.save()

    class Meta:
        app_label = 'usuarios'

