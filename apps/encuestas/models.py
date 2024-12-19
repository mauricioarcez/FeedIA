import random
from django.db import models
from apps.usuarios.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from .ai import SentimentAnalyzer
import logging

class Encuesta(models.Model):
    negocio = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='encuestas_recibidas',
        limit_choices_to={'user_type': 'business'}
    )
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='encuestas_realizadas',
        limit_choices_to={'user_type': 'common'},
        null=True,
        blank=True
    )
    experiencia_general = models.IntegerField(null=True, blank=True)
    atencion_servicio = models.IntegerField(null=True, blank=True)
    recomendaciones = models.TextField(max_length=500, blank=True, null=True)
    tipo_cliente = models.CharField(
        max_length=20,
        choices=[
            ("primera", "Primera vez"),
            ("frecuente", "Cliente frecuente"),
            ("ocasional", "Cliente ocasional"),
        ],
        null=True,
        blank=True
    )
    respuesta_anonima = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    codigo_temporal = models.CharField(max_length=4, blank=True, null=True)
    encuesta_completada = models.BooleanField(default=False)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    sentimiento = models.CharField(max_length=50, blank=True, null=True)
    confianza_sentimiento = models.FloatField(null=True, blank=True)

    def generar_codigo(self):
        """Genera un código aleatorio de 4 dígitos para cada negocio."""
        # Asegurarse de que el código sea único dentro del negocio
        while True:
            self.codigo_temporal = str(random.randint(1000, 9999))
            # Verificar que el código no exista ya en este negocio
            if not Encuesta.objects.filter(codigo_temporal=self.codigo_temporal, negocio=self.negocio).exists():
                break
        # Establecer una fecha de expiración, por ejemplo 24 horas después de la creación
        self.fecha_expiracion = timezone.now() + timedelta(hours=24)
        self.save()

    def __str__(self):
        return f"Encuesta para {self.negocio.nombre_negocio} por {self.usuario} - {self.fecha_respuesta.date()}"

    def codigo_expirado(self):
        """Verifica si el código de la encuesta ha expirado."""
        return timezone.now() > self.fecha_expiracion

    def marcar_codigo_como_usado(self):
        """Marca el código como usado, cambiando la fecha de expiración a ahora."""
        self.fecha_expiracion = timezone.now()  # Marcar el código como usado al expirar
        self.save()

    def analizar_sentimiento(self):
        """Analiza el sentimiento de las recomendaciones usando IA."""
        if not self.recomendaciones:
            return None
        
        try:
            analyzer = SentimentAnalyzer()
            resultado = analyzer.analyze_with_cache([self.recomendaciones])[0]
            
            # Guardamos el resultado del análisis
            self.sentimiento = resultado['label']
            self.confianza_sentimiento = resultado['score']
            self.save()
            
            return resultado
        except Exception as e:
            logging.error(f"Error al analizar sentimiento: {str(e)}")
            return None
