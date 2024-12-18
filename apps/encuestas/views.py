# encuestas/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Encuesta, CustomUser
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
        # Obtener la encuesta por el código temporal
        encuesta = Encuesta.objects.get(codigo_temporal=codigo)
    except Encuesta.DoesNotExist:
        messages.error(request, 'Código de encuesta no válido o expirado.')
        return redirect('home')  # Redirige al home si el código no es válido o ha expirado

    # Verificar si la encuesta ya fue completada
    if encuesta.encuesta_completada:
        messages.error(request, 'Esta encuesta ya ha sido completada.')
        return redirect('home')

    # Verificar si el código ha expirado
    if encuesta.codigo_expirado():
        messages.error(request, 'El código de la encuesta ha expirado.')
        return redirect('home')  # Redirigir a la página de inicio si el código ha expirado

    if request.method == 'POST':
        form = EncuestaForm(request.POST)
        if form.is_valid():
            encuesta_respuesta = form.save(commit=False)
            encuesta_respuesta.usuario = request.user  # Asignamos al usuario que está completando la encuesta
            encuesta_respuesta.encuesta = encuesta  # Asignamos la encuesta correspondiente
            encuesta_respuesta.save()

            # Marcar la encuesta como completada y evitar que se responda nuevamente
            encuesta.encuesta_completada = True
            encuesta.marcar_codigo_como_usado()

            # Sumar puntos
            request.user.puntos += 2  # Suponiendo que 2 puntos se asignan por completar la encuesta
            request.user.save()

            messages.success(request, '¡Gracias por completar la encuesta! Se te han sumado 2 puntos.')
            return redirect('home')  # Redirigir a la página de inicio después de completar la encuesta
    else:
        form = EncuestaForm()

    return render(request, 'encuestas/completar_encuesta.html', {'form': form, 'encuesta': encuesta})

# ------------------------------------------------------------------------------------------------

@login_required
def ver_encuestas(request):
    """Vista para que el negocio vea todas las encuestas que ha creado"""
    if request.user.is_business_user():
        encuestas = Encuesta.objects.filter(negocio=request.user)
        return render(request, 'encuestas/ver_encuestas.html', {'encuestas': encuestas})
    else:
        return redirect('home')


