import random
from django.db import models
from django.utils import timezone
from .ai import SentimentAnalyzer
import string
import logging
from apps.usuarios.models import CustomUser

logger = logging.getLogger(__name__)

class Empleado(models.Model):
    negocio = models.ForeignKey(
        'usuarios.CustomUser',
        on_delete=models.CASCADE,
        related_name='empleados',
        limit_choices_to={'user_type': 'business'}
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        ordering = ['nombre', 'apellido']
        unique_together = ['negocio', 'nombre', 'apellido']

class Encuesta(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('recurrente', 'Recurrente'),
        ('ocasional', 'Ocasional'),
    ]

    SENTIMIENTO_CHOICES = [
        ('POS', 'Positivo'),
        ('NEU', 'Neutral'),
        ('NEG', 'Negativo'),
    ]

    usuario = models.ForeignKey(
        'usuarios.CustomUser',
        on_delete=models.CASCADE,
        related_name='encuestas_creadas'
    )
    negocio = models.ForeignKey(
        'usuarios.CustomUser',
        on_delete=models.CASCADE,
        related_name='encuestas_negocio'
    )
    codigo_temporal = models.CharField(max_length=4, unique=True, null=True, blank=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    encuesta_completada = models.BooleanField(default=False)
    sentimiento = models.CharField(
        max_length=3,
        choices=SENTIMIENTO_CHOICES,
        null=True,
        blank=True
    )
    
    # Campos nuevos para el formulario
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        null=False,
        blank=True
    )
    respuesta_anonima = models.BooleanField(default=False)
    experiencia_general = models.IntegerField(null=True, blank=True)
    atencion_servicio = models.IntegerField(null=True, blank=True)
    recomendaciones = models.TextField(null=True, blank=True)
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encuestas'
    )
    hashtag = models.CharField(
        max_length=30,  # Longitud máxima para el hashtag
        null=True,
        blank=True,
        help_text="Una palabra que defina tu experiencia (sin el símbolo #)"
    )

    def generar_codigo_temporal(self):
        """Genera un código único de 4 dígitos"""
        while True:
            codigo = ''.join(random.choices(string.digits, k=4))
            if not Encuesta.objects.filter(codigo_temporal=codigo).exists():
                self.codigo_temporal = codigo
                self.save()
                break

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
            
            # Mapear las etiquetas del modelo a nuestro formato
            sentiment_mapping = {
                'POS': 'POS',
                'NEG': 'NEG',
                'NEU': 'NEU'
            }
            
            self.sentimiento = sentiment_mapping.get(resultado['label'], 'NEU')
            self.save()
            
            return resultado
        except Exception as e:
            logger.error(f"Error al analizar sentimiento: {str(e)}", exc_info=True)
            return None

    def clean(self):
        super().clean()
        if self.hashtag:
            # Eliminar espacios y caracteres especiales
            self.hashtag = self.hashtag.strip().replace(' ', '')
            # Eliminar el símbolo # si el usuario lo incluyó
            self.hashtag = self.hashtag.replace('#', '')

