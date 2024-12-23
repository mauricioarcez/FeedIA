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
    experiencia_general = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '5'
        })
    )
    
    atencion_servicio = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '5'
        })
    )

    class Meta:
        model = Encuesta
        fields = [
            'tipo_cliente',
            'experiencia_general',
            'atencion_servicio',
            'recomendaciones',
            'hashtag',
            'respuesta_anonima'
        ]
        widgets = {
            'tipo_cliente': forms.Select(attrs={'class': 'form-control'}),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tu sinceridad es muy importante para nosotros. No te preocupes, es anonimo.'
            }),
            'hashtag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Rapido'
            }),
            'respuesta_anonima': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'tipo_cliente': '¿Qué tipo de cliente eres?',
            'experiencia_general': 'Califica tu experiencia general (1-5)',
            'atencion_servicio': 'Califica la atención del servicio (1-5)',
            'recomendaciones': 'Comentanos tu experiencia o sugerencias',
            'hashtag': 'Define el servicio en una palabra'
        }

    def save(self, commit=True):
        encuesta = super().save(commit=False)
        if commit:
            encuesta.save()
        return encuesta

