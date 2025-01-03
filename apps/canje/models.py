from django.db import models
from django.conf import settings

class Canje(models.Model):
    negocio = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntos_requeridos = models.IntegerField()
    titulo = models.CharField(max_length=40, null=False)
    descripcion = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='canjes/', blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.puntos_requeridos} puntos"
