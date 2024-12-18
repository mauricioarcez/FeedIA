# encuestas/forms.py
from django import forms
from .models import Encuesta

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ['experiencia_general', 'atencion_servicio', 'recomendaciones', 'tipo_cliente', 'respuesta_anonima']
        widgets = {
            'experiencia_general': forms.HiddenInput(),
            'atencion_servicio': forms.HiddenInput(),
            'recomendaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tus recomendaciones o mejoras (máximo 500 caracteres)',
                'rows': 4,
                'maxlength': 500
            }),
            'tipo_cliente': forms.Select(attrs={'class': 'form-control'}),
            'respuesta_anonima': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        encuesta = super().save(commit=False)
        if commit:
            encuesta.save()
        return encuesta

