# encuestas/models.py
from django.db import models

class Encuesta(models.Model):
    """Modelo para las encuestas que pueden ser generadas por un negocio"""
    codigo = models.CharField(max_length=10, unique=True)  # Código único para acceder a la encuesta
    nombre = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre


class Pregunta(models.Model):
    """Modelo para las preguntas de una encuesta"""
    encuesta = models.ForeignKey(Encuesta, related_name="preguntas", on_delete=models.CASCADE)
    texto = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=[('texto', 'Texto'), ('opciones', 'Opciones')])

    def __str__(self):
        return self.texto

