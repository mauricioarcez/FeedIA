import random
from django.db import models
from usuarios.models import CustomUser
from django.utils import timezone
from datetime import timedelta

class Encuesta(models.Model):
    negocio = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='encuestas_recibidas',
        limit_choices_to={'user_type': 'business'}  # Limita a usuarios tipo negocio
    )
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='encuestas_realizadas',
        limit_choices_to={'user_type': 'common'},
        null=True,
        blank=True
    )
    experiencia_general = models.IntegerField()  # Escala de 1-10
    atencion_servicio = models.IntegerField()  # Escala de 1-10
    recomendaciones = models.TextField(max_length=500, blank=True, null=True)
    tipo_cliente = models.CharField(
        max_length=20,
        choices=[
            ("primera", "Primera vez"),
            ("frecuente", "Cliente frecuente"),
            ("ocasional", "Cliente ocasional"),
        ]
    )
    respuesta_anonima = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    codigo_temporal = models.CharField(max_length=4, blank=True, null=True)  # Código único temporal
    encuesta_completada = models.BooleanField(default=False)  # Indica si la encuesta ya fue completada
    fecha_expiracion = models.DateTimeField(null=True, blank=True)  # Fecha de expiración del código

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
