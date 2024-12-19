from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def business_required(view_func):
    """Decorador para vistas que requieren usuario tipo negocio"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_business_user():
            messages.error(request, 'Acceso denegado. Se requiere cuenta de negocio.')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def common_user_required(view_func):
    """Decorador para vistas que requieren usuario común"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_common_user():
            messages.error(request, 'Acceso denegado. Se requiere cuenta de usuario común.')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 