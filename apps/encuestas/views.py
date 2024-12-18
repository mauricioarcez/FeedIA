# encuestas/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.usuarios.models import CustomUser
from .models import Encuesta
from .forms import EncuestaForm

# ------------------------------------------------------------------------------------------------

@login_required
def crear_encuesta(request):
    """Vista para que el negocio cree una nueva encuesta con un código temporal"""
    if request.user.user_type != 'business':
        messages.error(request, 'Solo los negocios pueden crear encuestas.')
        return redirect('home')  # Redirigir si el usuario no es de tipo 'business'

    if request.method == 'POST':
        encuesta = Encuesta(
            negocio=request.user,
            usuario=None  # Se asignará cuando alguien complete la encuesta
        )
        encuesta.generar_codigo()
        encuesta.save()
        messages.success(request, f'Encuesta creada con el código: {encuesta.codigo_temporal}')
        return redirect('encuestas:ver_encuestas')
    return render(request, 'encuestas/crear_encuesta.html')


# ------------------------------------------------------------------------------------------------

@login_required
def completar_encuesta(request, codigo):
    """Vista para completar la encuesta a partir de un código temporal"""
    try:
        encuesta = Encuesta.objects.get(codigo_temporal=codigo)
        
        if request.method == 'POST':
            form = EncuestaForm(request.POST, instance=encuesta)
            if form.is_valid():
                encuesta_respuesta = form.save(commit=False)
                encuesta_respuesta.usuario = request.user
                encuesta_respuesta.save()
                
                encuesta.encuesta_completada = True
                encuesta.marcar_codigo_como_usado()
                
                # Sumar puntos al usuario
                request.user.puntos += 2
                request.user.save()
                
                messages.success(request, '¡Gracias por completar la encuesta! Se te han sumado 2 puntos.')
                return redirect('usuarios:home')
        else:
            form = EncuestaForm(instance=encuesta)
        
        return render(request, 'encuestas/completar_encuesta.html', {'form': form, 'encuesta': encuesta})
    except Encuesta.DoesNotExist:
        messages.error(request, 'Código de encuesta no válido o expirado.')
        return redirect('usuarios:home')

# ------------------------------------------------------------------------------------------------

@login_required
def ver_encuestas(request):
    """Vista para que el negocio vea todas las encuestas que ha creado"""
    if request.user.is_business_user():
        encuestas = Encuesta.objects.filter(negocio=request.user)
        return render(request, 'encuestas/ver_encuestas.html', {'encuestas': encuestas})
    else:
        return redirect('home')
    
# ------------------------------------------------------------------------------------------------
@login_required
def ingresar_codigo(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        negocio_id = request.POST.get('negocio')
        try:
            # Verificar que el código pertenezca al negocio seleccionado
            encuesta = Encuesta.objects.get(
                codigo_temporal=codigo,
                negocio_id=negocio_id,
                encuesta_completada=False
            )
            return redirect('encuestas:completar_encuesta', codigo=codigo)
        except Encuesta.DoesNotExist:
            messages.error(request, 'Código no válido para el negocio seleccionado.')
            return redirect('encuestas:ingresar_codigo')
    
    # Obtener lista de negocios para el select
    negocios = CustomUser.objects.filter(user_type='business')
    return render(request, 'encuestas/ingresar_codigo.html', {'negocios': negocios})


