# encuestas/forms.py
from django import forms
from .models import Encuesta

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ['calificacion_general', 'calificacion_servicio', 'recomendaciones']
        widgets = {
            'calificacion_general': forms.NumberInput(attrs={
                'min': 1, 'max': 10, 'step': 1, 'class': 'form-control',
                'placeholder': 'Califica tu experiencia (1-10)'}),
            'calificacion_servicio': forms.NumberInput(attrs={
                'min': 1, 'max': 10, 'step': 1, 'class': 'form-control',
                'placeholder': 'Califica el servicio (1-10)'}),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Escribe tus recomendaciones o mejoras (máximo 500 caracteres)',
                'rows': 4, 'maxlength': 500}),
        }

    def save(self, commit=True):
        encuesta = super().save(commit=False)
        if commit:
            encuesta.save()
        return encuesta

