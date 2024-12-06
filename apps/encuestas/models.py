from django.db import models
import uuid
# Create your models here.

class Encuesta(models.Model):
    negocio = models.CharField(max_length=100)  # Nombre del negocio
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creada_el = models.DateTimeField(auto_now_add=True)
    usada = models.BooleanField(default=False)

    def __str__(self):
        return f"Encuesta {self.codigo} - {'Usada' if self.usada else 'Disponible'}"