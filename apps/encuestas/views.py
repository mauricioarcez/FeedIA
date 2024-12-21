# encuestas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.usuarios.models import CustomUser
from .models import Encuesta, Empleado
from .forms import EncuestaForm, EmpleadoForm
from datetime import timedelta
from .services import ReportesService

# ------------------------------------------------------------------------------------------------

@login_required
def crear_encuesta(request):
    """Vista para crear una nueva encuesta"""
    if not request.user.is_business_user():
        messages.error(request, 'Solo los negocios pueden crear encuestas.')
        return redirect('home')

    if request.method == 'POST':
        try:
            empleado_id = request.POST.get('empleado')
            empleado = Empleado.objects.get(id=empleado_id, negocio=request.user)
            
            encuesta = Encuesta.objects.create(
                negocio=request.user,
                usuario=request.user,
                empleado=empleado,
                fecha_respuesta=timezone.now(),
                fecha_expiracion=timezone.now() + timedelta(hours=24)
            )
            
            encuesta.generar_codigo_temporal()
            messages.success(request, f'Encuesta creada exitosamente. Código: {encuesta.codigo_temporal}')
            return redirect('encuestas:ver_encuestas')
            
        except Exception as e:
            print(f"Error al crear encuesta: {str(e)}")
            messages.error(request, 'Error al crear la encuesta')
            return redirect('encuestas:crear_encuesta')
    
    # Obtener empleados activos del negocio
    empleados = Empleado.objects.filter(negocio=request.user, activo=True)
    return render(request, 'encuestas/crear_encuesta.html', {'empleados': empleados})


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
                encuesta_respuesta.save()  # Primero guardamos para tener el ID
                
                # Analizar sentimiento y asegurarnos que se guarde
                resultado = encuesta_respuesta.analizar_sentimiento()
                print(f"Resultado del análisis: {resultado}")  # Debug
                
                if resultado:
                    encuesta_respuesta.sentimiento = resultado['label']
                    encuesta_respuesta.save()  # Guardar de nuevo con el sentimiento
                
                encuesta_respuesta.encuesta_completada = True
                encuesta_respuesta.marcar_codigo_como_usado()
                
                # Sumar puntos al usuario
                request.user.puntos += 2
                request.user.save()
                
                messages.success(request, '¡Gracias por completar la encuesta! Se te han sumado 2 puntos.')
                return redirect('usuarios:home')
        else:
            form = EncuestaForm(instance=encuesta)
        
        return render(request, 'encuestas/completar_encuesta.html', {
            'form': form, 
            'encuesta': encuesta
        })
    except Encuesta.DoesNotExist:
        messages.error(request, 'Código de encuesta no válido o expirado.')
        return redirect('usuarios:home')

# ------------------------------------------------------------------------------------------------

@login_required
def ver_encuestas(request):
    """Vista para ver todas las encuestas generadas por el negocio"""
    if request.user.is_business_user():
        # Filtrar encuestas donde el negocio es el usuario actual y ordenar por fecha descendente
        encuestas = Encuesta.objects.filter(negocio=request.user).order_by('-fecha_respuesta')
        
        # Contar encuestas completadas
        encuestas_completadas = encuestas.filter(encuesta_completada=True).count()
        
        context = {
            'encuestas': encuestas,
            'total_encuestas': encuestas.count(),
            'encuestas_completadas': encuestas_completadas
        }
        
        return render(request, 'encuestas/ver_encuestas.html', context)
    else:
        messages.error(request, "No tienes permiso para ver esta página")
        return redirect('usuarios:home')

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

# ------------------------------------------------------------------------------------------------

@login_required
def administrar_empleados(request):
    if not request.user.is_business_user():
        messages.error(request, "Acceso denegado")
        return redirect('home')
        
    empleados = Empleado.objects.filter(negocio=request.user)
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            empleado = form.save(commit=False)
            empleado.negocio = request.user
            empleado.save()
            messages.success(request, "Empleado agregado exitosamente")
            return redirect('encuestas:administrar_empleados')
    else:
        form = EmpleadoForm()
    
    return render(request, 'negocios/administrar_empleados.html', {
        'empleados': empleados,
        'form': form
    })

# ------------------------------------------------------------------------------------------------

@login_required
def toggle_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id, negocio=request.user)
    empleado.activo = not empleado.activo
    empleado.save()
    return redirect('encuestas:administrar_empleados')

# ------------------------------------------------------------------------------------------------

@login_required
def reportes(request):
    orden = request.GET.get('orden', 'calificacion_desc')
    service = ReportesService(request.user.id)
    ranking_empleados = service.get_ranking_empleados(orden)
    
    # Obtener totales de opiniones
    total_opiniones = service.get_total_opiniones()
    
    context = {
        'ranking_empleados': ranking_empleados,
        'orden': orden,
        'total_opiniones_positivas': total_opiniones['positivas'],
        'total_opiniones_negativas': total_opiniones['negativas']
    }
    return render(request, 'encuestas/reportes.html', context)


