from django.contrib import admin
from .models import Empleado, Encuesta

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'negocio', 'activo')
    list_filter = ('activo', 'negocio')
    search_fields = ('nombre', 'apellido')

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'negocio', 'atencion_servicio', 'encuesta_completada', 'fecha_respuesta')
    list_filter = ('encuesta_completada', 'negocio')
    search_fields = ('empleado__nombre', 'negocio__nombre_negocio')
