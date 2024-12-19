from django.core.cache import cache
from django.db.models import Avg, Count, Q
from django.db.models.functions import Coalesce
from typing import Dict, List
from .models import Encuesta, Empleado
import logging

logger = logging.getLogger(__name__)

class ReportesService:
    CACHE_TTL = 3600  # 1 hora en segundos
    
    def __init__(self, negocio_id: int):
        self.negocio_id = negocio_id
    
    def get_ranking_empleados(self) -> List[Dict]:
        cache_key = f"reportes_ranking_{self.negocio_id}"
        result = cache.get(cache_key)
        
        if result is None:
            empleados = Empleado.objects.filter(
                negocio_id=self.negocio_id
            ).annotate(
                total_encuestas=Count('encuestas'),
                opiniones_positivas=Count('encuestas', filter=Q(encuestas__sentimiento='POS')),
                opiniones_negativas=Count('encuestas', filter=Q(encuestas__sentimiento='NEG')),
                calificacion_promedio=Coalesce(
                    Avg('encuestas__atencion_servicio'),
                    0.0
                )
            ).filter(
                total_encuestas__gt=0
            )
            
            result = [{
                'nombre': f"{emp.nombre} {emp.apellido}",
                'total_encuestas': emp.total_encuestas,
                'opiniones_positivas': emp.opiniones_positivas,
                'opiniones_negativas': emp.opiniones_negativas,
                'calificacion_promedio': float(emp.calificacion_promedio),
                'sentimiento_general': 'POS' if emp.opiniones_positivas >= emp.opiniones_negativas else 'NEG'
            } for emp in empleados]
            
            result.sort(key=lambda x: x['calificacion_promedio'], reverse=True)
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