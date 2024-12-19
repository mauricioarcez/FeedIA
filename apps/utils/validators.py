import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    """Validador para números de teléfono"""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError('Número de teléfono inválido.')

def validate_password_strength(value):
    """Validador para contraseñas seguras"""
    if len(value) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('La contraseña debe contener al menos una mayúscula.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('La contraseña debe contener al menos una minúscula.')
    if not re.search(r'\d', value):
        raise ValidationError('La contraseña debe contener al menos un número.') 