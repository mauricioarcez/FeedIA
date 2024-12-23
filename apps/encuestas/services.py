from django.core.cache import cache
from django.db.models import Avg, Count, Q, Case, When, FloatField
from django.db.models.functions import Coalesce
from typing import Dict, List
import plotly.graph_objects as go
import plotly.utils
import json
from apps.encuestas.models import Encuesta, Empleado

# --------------------------------------------------------------------------------------------
class ReportesService:
    CACHE_TTL = 3600  # 1 hora en segundos
    
    def __init__(self, negocio_id: int):
        self.negocio_id = negocio_id
    
    def get_ranking_empleados(self, orden: str = 'calificacion_desc') -> List[Dict]:
        cache_key = f"reportes_ranking_{self.negocio_id}_{orden}"
        result = cache.get(cache_key)
        
        if result is None:
            empleados = Empleado.objects.filter(
                negocio_id=self.negocio_id,
                activo=True,
                encuestas__encuesta_completada=True  # Solo encuestas completadas
            ).annotate(
                total_encuestas=Count(
                    'encuestas',
                    filter=Q(
                        encuestas__encuesta_completada=True,
                        encuestas__atencion_servicio__isnull=False
                    )
                ),
                calificacion_promedio=Coalesce(
                    Avg(
                        Case(
                            When(
                                encuestas__encuesta_completada=True,
                                encuestas__atencion_servicio__isnull=False,
                                then='encuestas__atencion_servicio'
                            ),
                            output_field=FloatField(),
                        )
                    ),
                    0.0
                )
            ).filter(total_encuestas__gt=0)
            
            # Debug: Imprimir valores para verificar
            print("Empleados y calificaciones:")
            for emp in empleados:
                print(f"Empleado: {emp.nombre}, Total: {emp.total_encuestas}, Promedio: {emp.calificacion_promedio}")
                # Imprimir todas las calificaciones del empleado
                calificaciones = emp.encuestas.filter(
                    encuesta_completada=True
                ).values_list('atencion_servicio', flat=True)
                print(f"Calificaciones individuales: {list(calificaciones)}")
            
            empleados_list = list(empleados)
            
            # Ordenamiento
            reverse = orden.endswith('_desc')
            if orden.startswith('total'):
                key = lambda x: (x.total_encuestas, x.calificacion_promedio)
            else:  # orden por calificación
                key = lambda x: (x.calificacion_promedio, x.total_encuestas)
            
            empleados_list.sort(key=key, reverse=reverse)
            
            # Tomar solo el top 2 y el último
            if len(empleados_list) > 3:
                empleados_list = empleados_list[:2] + [empleados_list[-1]]
            
            result = [{
                'nombre': f"{emp.nombre} {emp.apellido}",
                'total_encuestas': emp.total_encuestas,
                'calificacion_promedio': round(float(emp.calificacion_promedio), 1),
                'is_last': emp == empleados_list[-1] if empleados_list else False
            } for emp in empleados_list]
            
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result

    def get_sentimientos_totales(self) -> Dict:
        cache_key = f"reportes_sentimientos_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            encuestas = Encuesta.objects.filter(
                negocio_id=self.negocio_id,
                encuesta_completada=True,
                sentimiento__isnull=False
            )
            result = {
                'POS': encuestas.filter(sentimiento='POS').count(),
                'NEG': encuestas.filter(sentimiento='NEG').count()
            }
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result 


    def get_sentimientos_graph(self) -> str:
        sentimientos = self.get_sentimientos_totales()
        
        fig = go.Figure(data=[
            go.Bar(
                y=['Positivas', 'Negativas'],
                x=[sentimientos['POS'], sentimientos['NEG']],
                marker_color=['#00A9B8', '#e74c3c'],
                orientation='h',
                text=[sentimientos['POS'], sentimientos['NEG']],
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(
                    color='white',
                    size=12,
                    family='Poppins'
                )
            )
        ])

        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins",
            height=150,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(
                showticklabels=True,
                tickfont=dict(size=10),
                showgrid=False
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1,
                showgrid=False
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_total_opiniones(self) -> Dict[str, int]:
        cache_key = f"total_opiniones_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            result = {
                'positivas': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    sentimiento='POS'
                ).count(),
                'negativas': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    sentimiento='NEG'
                ).count()
            }
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result

    def get_total_genero(self) -> Dict[str, int]:
        cache_key = f"total_genero_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            result = {
                'masculino': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__genero='M'  # Usamos el género del usuario que creó la encuesta
                ).count(),
                'femenino': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__genero='F'  # Usamos el género del usuario que creó la encuesta
                ).count()
            }
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result

    def get_distribucion_generos(self):
        """Obtiene la distribución de géneros de los encuestados."""
        return (
            Encuesta.objects
            .filter(
                negocio_id=self.negocio_id,
                encuesta_completada=True,
                usuario__genero__isnull=False
            )
            .values('usuario__genero')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

    def get_generos_graph(self) -> str:
        generos = self.get_total_genero()
        
        fig = go.Figure(data=[
            go.Bar(
                y=['Masculino', 'Femenino'],
                x=[generos['masculino'], generos['femenino']],
                marker_color=['#4a90e2', '#e84393'],
                orientation='h',
                text=[generos['masculino'], generos['femenino']],
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(
                    color='white',
                    size=12,
                    family='Poppins'
                )
            )
        ])

        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins",
            height=150,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(
                showticklabels=True,
                tickfont=dict(size=10),
                showgrid=False
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1,
                showgrid=False
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_edades_totales(self) -> Dict[str, int]:
        cache_key = f"total_edades_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            result = {
                'menor_18': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__edad__lt=18
                ).count(),
                '19_25': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__edad__gte=19,
                    usuario__edad__lte=25
                ).count(),
                '26_35': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__edad__gte=26,
                    usuario__edad__lte=35
                ).count(),
                '36_50': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__edad__gte=36,
                    usuario__edad__lte=50
                ).count(),
                'mayor_60': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__edad__gt=60
                ).count()
            }
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result

    def get_edades_graph(self) -> str:
        edades = self.get_edades_totales()
        
        # Definir el orden de las categorías
        categorias = ['< 18', '19-25', '26-35', '36-50', '> 60']
        valores = [
            edades['menor_18'],
            edades['19_25'],
            edades['26_35'],
            edades['36_50'],
            edades['mayor_60']
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                y=categorias,  # Categorías de edad
                x=valores,     # Cantidad de encuestados
                marker_color=['#FF9F43', '#FF6B6B', '#4834D4', '#2C3E50', '#26DE81'],
                orientation='h',
                text=valores,
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(
                    color='white',
                    size=12,
                    family='Poppins'
                )
            )
        ])

        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins",
            height=150,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(
                showticklabels=True,
                tickfont=dict(size=10),
                showgrid=False
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1,
                showgrid=False
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)