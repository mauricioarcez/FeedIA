from datetime import datetime, timedelta
import random
import string

def generate_unique_code(length=6):
    """Genera un código único alfanumérico"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def calculate_expiration_date(hours=24):
    """Calcula fecha de expiración"""
    return datetime.now() + timedelta(hours=hours)

def format_points(points):
    """Formatea puntos para mostrar"""
    if points >= 1000:
        return f"{points/1000:.1f}K"
    return str(points)

def calculate_reward_points(purchase_amount):
    """Calcula puntos de recompensa basado en monto"""
    base_points = int(purchase_amount * 0.1)  # 10% del monto en puntos
    return min(base_points, 100)  # Máximo 100 puntos por compra 