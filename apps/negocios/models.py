from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator, RegexValidator

class Negocio(AbstractUser):
    """
    Modelo que representa a un negocio registrado en el sistema.
    """
    correo_dueño = models.EmailField(
        max_length=70,
        unique=True,  # El correo del dueño será único
        blank=False,  # El correo es obligatorio
        null=False, 
        validators=[EmailValidator()],
        help_text="Correo electrónico del dueño o negocio"
    )
    nombre_negocio = models.CharField(
        max_length=50,
        blank=False,  # El nombre del negocio es obligatorio
        null=False,  # No puede ser nulo
        help_text="Nombre del negocio"
    )
    provincia = models.CharField(
        max_length=30,
        blank=False,  # La provincia es obligatoria
        null=False,  # No puede ser nula
        help_text="Provincia donde se encuentra el negocio"
    )
    categoria_negocio = models.CharField(
        max_length=30,
        blank=False,  # La categoría es obligatoria
        null=False,  # No puede ser nula
        help_text="Categoría del negocio"
    )
    direccion = models.CharField(
        max_length=70,
        blank=False,  # La dirección es obligatoria
        null=False,  # No puede ser nula
        help_text="Dirección completa del negocio"
    )
    telefono = models.CharField(
        max_length=10,
        blank=False,  # El teléfono es obligatorio
        null=False,  # No puede ser nulo
        validators=[ 
            RegexValidator(
                regex=r'^\d{10}$',
                message="El número de teléfono debe ser de 10 dígitos."
            )
        ],
        help_text="Teléfono de contacto del negocio"
    )

    # Asegurarse de que las relaciones 'groups' y 'user_permissions' no entren en conflicto
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='negocios_set',  # Cambiar el related_name para evitar conflictos
        blank=True,
        help_text="Grupos a los que pertenece el negocio"
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='negocios_permissions_set',  # Cambiar el related_name para evitar conflictos
        blank=True,
        help_text="Permisos específicos para este negocio"
    )

    def __str__(self):
        return self.nombre_negocio