# encuestas/forms.py

from django import forms
from .models import Encuesta, Pregunta

class EncuestaForm(forms.ModelForm):
    """Formulario para generar una encuesta"""
    class Meta:
        model = Encuesta
        fields = ['nombre']


class PreguntaForm(forms.ModelForm):
    """Formulario para agregar preguntas a una encuesta"""
    class Meta:
        model = Pregunta
        fields = ['texto', 'tipo']
