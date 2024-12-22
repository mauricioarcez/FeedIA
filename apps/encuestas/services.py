from django.core.cache import cache
from django.db.models import Avg, Count, Q
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
                activo=True
            ).annotate(
                total_encuestas=Count('encuestas'),
                calificacion_promedio=Coalesce(
                    Avg('encuestas__atencion_servicio'),
                    0.0
                )
            )
            
            # Convertir a lista y ordenar según el criterio seleccionado
            empleados_list = list(empleados)
            
            # Definir la clave y dirección de ordenamiento
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
                'calificacion_promedio': float(emp.calificacion_promedio),
                'is_last': emp == empleados_list[-1]
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
        """Genera gráfico de sentimientos con Plotly"""
        sentimientos = self.get_sentimientos_totales()
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Sentimientos'],
                y=[sentimientos['POS']],
                name='Positivas',
                marker_color='#00A9B8',
                orientation='v'
            ),
            go.Bar(
                x=['Sentimientos'],
                y=[sentimientos['NEG']],
                name='Negativas',
                marker_color='#e74c3c',
                orientation='v'
            )
        ])

        fig.update_layout(
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins",
            margin=dict(l=50, r=50, t=30, b=30),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
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