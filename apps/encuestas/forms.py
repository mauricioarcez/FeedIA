# encuestas/forms.py
from django import forms
from .models import Encuesta, Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'})
        }

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = [
            'tipo_cliente',
            'respuesta_anonima',
            'experiencia_general',
            'atencion_servicio',
            'recomendaciones',
            'hashtag'
        ]
        widgets = {
            'tipo_cliente': forms.Select(attrs={'class': 'form-control'}),
            'experiencia_general': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'atencion_servicio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '¿Qué te pareció el servicio? ¿Qué podríamos mejorar?'
            }),
            'hashtag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Excelente, Rápido, Amable (sin #)',
                'pattern': '[A-Za-z0-9]+',
                'title': 'Ingresa una palabra sin espacios ni caracteres especiales'
            })
        }
        labels = {
            'tipo_cliente': '¿Qué tipo de cliente eres?',
            'respuesta_anonima': '¿Deseas que tu respuesta sea anónima?',
            'experiencia_general': 'Califica tu experiencia general (1-10)',
            'atencion_servicio': 'Califica la atención del servicio (1-10)',
            'recomendaciones': 'Déjanos tus comentarios',
            'hashtag': 'Define tu experiencia en una palabra'
        }

    def save(self, commit=True):
        encuesta = super().save(commit=False)
        if commit:
            encuesta.save()
        return encuesta

