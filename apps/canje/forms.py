class CanjeForm(forms.ModelForm):
    class Meta:
        model = Canje
        fields = ['titulo','descripcion', 'puntos_requeridos', 'imagen']
        widgets = {
            'descripcion': forms.TextInput(attrs={'placeholder': 'Descripción del Canje'}),
            'puntos_requeridos': forms.NumberInput(attrs={'placeholder': 'Puntos requeridos'}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Titulo del Canje'}),
            'imagen': forms.ClearableFileInput(attrs={'accept': 'image/*'}),  # Permitir solo imágenes
        }
