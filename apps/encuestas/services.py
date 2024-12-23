from django.core.cache import cache
from django.db.models import Avg, Count, Q, Case, When, FloatField
from django.db.models.functions import Coalesce
from typing import Dict, List
import plotly.graph_objects as go
import plotly.utils
import json
from apps.encuestas.models import Encuesta, Empleado
from django.utils import timezone
from datetime import date, timedelta

# --------------------------------------------------------------------------------------------
class ReportesService:
    CACHE_TTL = 3600  # 1 hora en segundos
    # Paleta de colores profesional
    COLORS = {
        'primary': '#1D3C59',    # Azul oscuro
        'secondary': '#00A9B8',  # Turquesa
        'accent1': '#4A90E2',    # Azul claro
        'accent2': '#F39C12',    # Naranja
        'accent3': '#E74C3C',    # Rojo
        'neutral': '#95A5A6'     # Gris
    }
    
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
                'NEU': encuestas.filter(sentimiento='NEU').count(),
                'NEG': encuestas.filter(sentimiento='NEG').count()
            }
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result 


    def get_sentimientos_graph(self) -> str:
        sentimientos = self.get_sentimientos_totales()
        
        fig = go.Figure(data=[
            go.Bar(
                y=['Positivas', 'Neutrales', 'Negativas'],
                x=[sentimientos['POS'], sentimientos['NEU'], sentimientos['NEG']],
                marker_color=[self.COLORS['secondary'], 
                            self.COLORS['neutral'], 
                            self.COLORS['accent3']],
                orientation='h',
                text=[sentimientos['POS'], sentimientos['NEU'], sentimientos['NEG']],
                textposition='inside',
                insidetextanchor='middle',
                textangle=0,
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
                'neutrales': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    sentimiento='NEU'
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
                    usuario__genero='M'
                ).count(),
                'femenino': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__genero='F'
                ).count(),
                'otro': Encuesta.objects.filter(
                    empleado__negocio_id=self.negocio_id,
                    usuario__genero='O'
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
                y=['Masculino', 'Femenino', 'Otro'],
                x=[generos['masculino'], generos['femenino'], generos['otro']],
                marker_color=[
                    self.COLORS['primary'], 
                    self.COLORS['secondary'],
                    self.COLORS['accent1']
                ],
                orientation='h',
                text=[generos['masculino'], generos['femenino'], generos['otro']],
                textposition='inside',
                insidetextanchor='middle',
                textangle=0,
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
            today = timezone.now().date()
            
            # Base query para encuestas completadas del negocio
            base_query = Encuesta.objects.filter(
                negocio_id=self.negocio_id,
                encuesta_completada=True
            ).values('usuario').distinct()  # Usar values() y distinct() en lugar de distinct(campo)
            
            result = {
                'menor_18': base_query.filter(
                    usuario__fecha_nacimiento__isnull=False,
                    usuario__fecha_nacimiento__gt=today - timedelta(days=18*365)
                ).count(),
                
                '19_25': base_query.filter(
                    usuario__fecha_nacimiento__isnull=False,
                    usuario__fecha_nacimiento__lte=today - timedelta(days=19*365),
                    usuario__fecha_nacimiento__gt=today - timedelta(days=25*365)
                ).count(),
                
                '26_35': base_query.filter(
                    usuario__fecha_nacimiento__isnull=False,
                    usuario__fecha_nacimiento__lte=today - timedelta(days=26*365),
                    usuario__fecha_nacimiento__gt=today - timedelta(days=35*365)
                ).count(),
                
                '36_50': base_query.filter(
                    usuario__fecha_nacimiento__isnull=False,
                    usuario__fecha_nacimiento__lte=today - timedelta(days=36*365),
                    usuario__fecha_nacimiento__gt=today - timedelta(days=50*365)
                ).count(),
                
                'mayor_60': base_query.filter(
                    usuario__fecha_nacimiento__isnull=False,
                    usuario__fecha_nacimiento__lte=today - timedelta(days=60*365)
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
                y=['< 18', '19-25', '26-35', '36-50', '> 60'],
                x=valores,
                marker_color=[
                    self.COLORS['accent1'],
                    self.COLORS['secondary'],
                    self.COLORS['primary'],
                    self.COLORS['accent2'],
                    self.COLORS['neutral']
                ],
                orientation='h',
                text=valores,
                textposition='inside',
                insidetextanchor='middle',
                textangle=0,
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

    def get_top_hashtags(self) -> List[Dict[str, any]]:
        cache_key = f"top_hashtags_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            # Obtener los hashtags de las encuestas completadas
            hashtags = Encuesta.objects.filter(
                negocio_id=self.negocio_id,
                encuesta_completada=True,
                hashtag__isnull=False
            ).exclude(
                hashtag=''
            ).values('hashtag').annotate(
                total=Count('hashtag')
            ).order_by('-total')[:3]  # Top 3 hashtags
            
            result = list(hashtags)
            cache.set(cache_key, result, self.CACHE_TTL)
        
        return result