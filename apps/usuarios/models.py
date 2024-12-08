from django.db import models
from django.core.validators import MinLengthValidator

# usuarios/models.py
from django.db import models
from django.core.validators import MinLengthValidator

class Usuario(models.Model):
    """
    Modelo para usuarios registrados en FeedIA.
    """

    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    username = models.CharField(
        max_length=30, 
        unique=True, 
        verbose_name="Nombre de usuario",
        help_text="Nombre único del usuario, máximo 30 caracteres."
    )
    password = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(6)],
        verbose_name="Contraseña",
        help_text="Contraseña del usuario, entre 6 y 30 caracteres."
    )
    genero = models.CharField(
        max_length=1, 
        choices=GENERO_CHOICES, 
        verbose_name="Género",
        help_text="Género del usuario (M: Masculino, F: Femenino)."
    )
    nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento",
        help_text="Fecha de nacimiento del usuario en formato DD-MM-YYYY."
    )
    puntos = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntos",
        help_text="Puntos acumulados por el usuario."
    )

    # Especificar el campo de autenticación
    USERNAME_FIELD = 'username'  # Usamos 'username' como el campo de autenticación
    REQUIRED_FIELDS = ['password', 'genero', 'nacimiento']  # Campos requeridos en la creación

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

