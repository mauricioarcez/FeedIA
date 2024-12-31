from django.core.cache import cache
from django.db.models import Avg, Count, Q, Case, When, FloatField
from django.db.models.functions import Coalesce, TruncDate
from typing import Dict, List
import plotly.graph_objects as go
import plotly.utils
import json
from apps.encuestas.models import Encuesta, Empleado
from django.utils import timezone
from datetime import timedelta

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
            
            for emp in empleados:
                # Imprimir todas las calificaciones del empleado
                calificaciones = emp.encuestas.filter(
                    encuesta_completada=True
                ).values_list('atencion_servicio', flat=True)
            
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
                showticklabels=False,
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
                showticklabels=False,
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
                y=categorias,
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
                showticklabels=False,  # Ocultar etiquetas del eje x
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

    def get_encuestas_por_dia(self, negocio) -> Dict[int, int]:
        """Obtiene la cantidad de encuestas por día del mes actual."""
        today = timezone.now().date()
        start_date = timezone.make_aware(timezone.datetime(today.year, today.month, 1))  # Primer día del mes actual
        end_date = timezone.make_aware(timezone.datetime(today.year, today.month, 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # Último día del mes actual

        # Realizar la consulta sin TruncDate
        encuestas_por_dia = (
            Encuesta.objects.filter(
                negocio_id=negocio.id,
                fecha_respuesta__range=[start_date, end_date]
            )
            .values('fecha_respuesta')  # Agrupar por la fecha original
            .annotate(total=Count('id'))  # Contar las encuestas
            .order_by('fecha_respuesta')  # Ordenar por fecha
        )

        # Crear un diccionario con días del mes y sus totales
        result = {day: 0 for day in range(1, 32)}
        for entry in encuestas_por_dia:
            if entry['fecha_respuesta'] is not None:  # Verificar que no sea None
                day = entry['fecha_respuesta'].day  # Acceder al atributo 'day'
                result[day] += entry['total']  # Sumar el total para ese día
        return result

    def get_encuestas_por_dia_graph(self, negocio) -> str:
        """Genera el gráfico de encuestas por día sin tarjeta de fondo."""
        encuestas_por_dia = self.get_encuestas_por_dia(negocio)  # Pasa el negocio aquí
        dias = list(encuestas_por_dia.keys())
        cantidades = list(encuestas_por_dia.values())

        # Crear el gráfico de líneas
        trace = go.Scatter(
            x=dias,
            y=cantidades,
            mode='lines+markers',
            marker=dict(color='#1D3C59')  # Cambiado a color solicitado
        )

        max_cantidad = max(cantidades) if cantidades else 0
        mitad_max = max_cantidad / 2

        layout = go.Layout(
            margin=dict(t=20, b=20, l=40, r=40),  # Ajusta los márgenes generales
            xaxis=dict(
                title='Día del Mes',
                titlefont=dict(
                    family='Poppins',  # Tipografía
                    size=10,           # Tamaño del título del eje X
                    color='var(--color-text)'  # Color del título
                ),
                tickvals=[1, 8, 15, 22, 31],  # Mostrar solo 4 números
                tickfont=dict(
                    family='Poppins',  # Tipografía para los ticks
                    size=10,           # Tamaño de la fuente de los ticks
                    color='var(--color-text)'  # Color de los ticks
                ),
                title_standoff=5,  # Reduce el espacio entre el título y el eje
                gridcolor='#F5F5F5'  # Cambiar el color del gridline
            ),
            yaxis=dict(
                title='Cantidad de Encuestas',
                titlefont=dict(
                    family='Poppins',  # Tipografía
                    size=10,           # Tamaño del título del eje Y
                    color='var(--color-text)'  # Color del título
                ),
                tickmode='array',
                tickvals=[0, mitad_max, max_cantidad + 1],  # Mostrar 0, mitad del máximo y máximo + 1
                tickfont=dict(
                    family='Poppins',  # Tipografía para los ticks
                    size=10,           # Tamaño de la fuente de los ticks
                ),
                title_standoff=5,  # Reduce el espacio entre el título y el eje
                gridcolor='#F5F5F5'  # Cambiar el color del gridline
            ),
            height=215  # Ajusta la altura del gráfico aquí también
        )

        fig = go.Figure(data=[trace], layout=layout)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_tipos_clientes_graph(self) -> str:
        """Genera un gráfico de barras apiladas horizontales que muestra el porcentaje de todos los tipos de clientes."""
        # Obtener los conteos de tipos de clientes
        nuevos = Encuesta.objects.filter(empleado__negocio_id=self.negocio_id, tipo_cliente='nuevo').count()
        recurrentes = Encuesta.objects.filter(empleado__negocio_id=self.negocio_id, tipo_cliente='recurrente').count()
        ocasionales = Encuesta.objects.filter(empleado__negocio_id=self.negocio_id, tipo_cliente='ocasional').count()

        # Datos para el gráfico
        conteos = [nuevos, recurrentes, ocasionales]
        total = sum(conteos)
        porcentajes = [(count / total * 100) if total > 0 else 0 for count in conteos]

        # Crear el gráfico de barras apiladas horizontales
        fig = go.Figure()

        # Agregar cada tipo de cliente como una barra apilada horizontal
        fig.add_trace(go.Bar(
            x=[porcentajes[0]],  # Porcentaje de nuevos
            y=['Clientes'],  # Solo una barra para todos los tipos
            name='Nuevos',
            orientation='h',  # Cambiar a orientación horizontal
            marker=dict(color=self.COLORS['accent1']),
            text=f"{porcentajes[0]:.1f}%",
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=12),
        ))

        fig.add_trace(go.Bar(
            x=[porcentajes[1]],  # Porcentaje de recurrentes
            y=['Clientes'],  # Solo una barra para todos los tipos
            name='Recurrentes',
            orientation='h',  # Cambiar a orientación horizontal
            marker=dict(color=self.COLORS['accent2']),
            text=f"{porcentajes[1]:.1f}%",
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=12),
        ))

        fig.add_trace(go.Bar(
            x=[porcentajes[2]],  # Porcentaje de ocasionales
            y=['Clientes'],  # Solo una barra para todos los tipos
            name='Ocasionales',
            orientation='h',  # Cambiar a orientación horizontal
            marker=dict(color=self.COLORS['accent3']),
            text=f"{porcentajes[2]:.1f}%",
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=12),
        ))

        # Configurar el layout del gráfico
        fig.update_layout(
            title='Tipos de Clientes',
            titlefont=dict(size=14, color=self.COLORS['primary']),
            barmode='stack',  # Establecer el modo de apilamiento
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins",
            height=150,
            margin=dict(l=20, r=20, t=20, b=20),  # Asegurando que el margen esté presente
            xaxis=dict(
                title='Porcentaje',
                titlefont=dict(size=12, color=self.COLORS['primary']),
                tickfont=dict(size=10),
                showgrid=False,
                range=[0, 100]
            ),
            yaxis=dict(
                title='Clientes',
                titlefont=dict(size=12, color=self.COLORS['primary']),
                tickfont=dict(size=10),
                showgrid=False
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)