from functools import wraps
import psutil
import logging

def check_memory(min_required_gb=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            memory = psutil.virtual_memory()
            required = min_required_gb * 1024 * 1024 * 1024
            
            if memory.available < required:
                logging.warning(f"Memoria baja: {memory.available/1024/1024/1024:.2f}GB disponible")
                # Intentar liberar memoria
                import gc
                gc.collect()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 