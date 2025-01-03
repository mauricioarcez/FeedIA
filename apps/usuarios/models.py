# apps/usuarios/models.py
import random
import string
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta, date
from django.utils import timezone
    
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('common', 'Usuario Común'),
        ('business', 'Usuario Negocio'),
    )
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    # Tipo de usuario (común o negocio)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    # Puntos del usuario (opcional para los usuarios comunes). Comienza con 5 puntos.
    puntos = models.PositiveIntegerField(default=5, blank=True, null=True)  # Puntos pueden ser nulos, ya que es opcional para usuarios comunes

    # Correo electrónico (único para evitar duplicados)
    correo = models.EmailField(max_length=60, unique=True, blank=False)  # Correo obligatorio, no nulo

    # Campos de negocio
    first_name = models.CharField(max_length=30, blank=False)  # Nombre obligatorio, no nulo
    last_name = models.CharField(max_length=30, blank=False)  # Apellido obligatorio, no nulo
    nombre_negocio = models.CharField(max_length=60, blank=True, null=True)  # Opcional para usuarios comunes
    
    # Campos de ubicación (requeridos para todos los usuarios)
    provincia = models.CharField(max_length=50, blank=False)
    ciudad = models.CharField(max_length=60, blank=False)
    
    # Campo de género - Ahora puede ser nulo para negocios
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        blank=True,  # Permitir valores en blanco
        null=True    # Permitir valores nulos
    )
    
    # Validación personalizada de correo
    def clean(self):
        super().clean()
        if self.correo:
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(pattern, self.correo):
                raise ValidationError('Formato de correo inválido.')
        
        # Validar que la ciudad y provincia no estén vacías
        if not self.ciudad:
            raise ValidationError('La ciudad es obligatoria.')
        if not self.provincia:
            raise ValidationError('La provincia es obligatoria.')
        
        # Validaciones específicas para usuario común
        if self.user_type == 'common':
            if not self.genero:
                raise ValidationError('El género es obligatorio para usuarios comunes.')
            if not self.fecha_nacimiento:
                raise ValidationError('La fecha de nacimiento es obligatoria para usuarios comunes.')
            
        

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

    fecha_nacimiento = models.DateField(null=True, blank=True)

    @property
    def edad(self):
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    class Meta:
        app_label = 'usuarios'

