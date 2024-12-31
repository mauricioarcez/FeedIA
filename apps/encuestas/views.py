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
from .ai import SentimentAnalyzer
from apps.encuestas.ai.sentiment_analyzer import SentimentAnalyzer
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------------------------

@login_required
def crear_encuesta(request):
    """Vista para crear una nueva encuesta"""
    if not request.user.is_business_user():
        messages.error(request, 'Solo los negocios pueden crear encuestas.')
        return redirect('inicio')

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
        encuesta = Encuesta.objects.select_related('empleado').get(codigo_temporal=codigo)
        print(f"Encuesta recuperada: {encuesta}")  # Esto mostrará todos los campos de la encuesta
        if request.method == 'POST':
            form = EncuestaForm(request.POST, instance=encuesta)
            if form.is_valid():
                encuesta_respuesta = form.save(commit=False)
                
                encuesta_respuesta.experiencia_general = form.cleaned_data['experiencia_general']
                encuesta_respuesta.atencion_servicio = form.cleaned_data['atencion_servicio']
                encuesta_respuesta.usuario = request.user
                encuesta_respuesta.empleado = encuesta.empleado
                

                # Aquí deberías llamar al análisis de sentimiento
                sentiment_analyzer = SentimentAnalyzer()
                resultado_sentimiento = sentiment_analyzer.analyze_with_cache([encuesta_respuesta.recomendaciones])
                
                # Verifica el resultado del análisis de sentimiento
                if resultado_sentimiento:
                    encuesta_respuesta.sentimiento = resultado_sentimiento[0]['label']  # Guarda la etiqueta de sentimiento
                
                encuesta_respuesta.encuesta_completada = True
                encuesta_respuesta.save()
                encuesta_respuesta.marcar_codigo_como_usado()
                
                # Sumar puntos al usuario
                request.user.puntos += 2
                request.user.save()

                messages.success(request, '¡Gracias por completar la encuesta! Se te han sumado 2 puntos.')
                return redirect('usuarios:home_common')
        else:
            form = EncuestaForm(instance=encuesta)
            print(form.errors)

        return render(request, 'encuestas/completar_encuesta.html', {
            'form': form, 
            'encuesta': encuesta
        })
    except Encuesta.DoesNotExist:
        messages.error(request, 'Código de encuesta no válido o expirado.')
        return redirect('usuarios:home_common')
                
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
        return redirect('usuarios:home_common')

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
            return redirect('encuestas:completar_encuesta', codigo=encuesta.codigo_temporal)
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
        return redirect('inicio')
        
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
    if not request.user.is_business_user():
        messages.error(request, "Acceso denegado")
        return redirect('home')
    
    service = ReportesService(request.user.id)
    negocio = request.user
    orden = request.GET.get('orden', 'calificacion_desc')
    
    context = {
        'total_opiniones': service.get_total_opiniones(),
        'ranking_empleados': service.get_ranking_empleados(orden),
        'orden': orden,
        'sentimientos_graph': service.get_sentimientos_graph(),
        'generos_graph': service.get_generos_graph(),
        'edades_graph': service.get_edades_graph(),
        'top_hashtags': service.get_top_hashtags(),
        'encuestas_por_dia': service.get_encuestas_por_dia(negocio),
        'encuestas_por_dia_graph': service.get_encuestas_por_dia_graph(negocio),
        'tipos_clientes_graph': service.get_tipos_clientes_graph(),  
    }
    
    return render(request, 'encuestas/reportes.html', context)


