from transformers import pipeline
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging
import time
import psutil
from django.conf import settings
from apps.utils.constants import SENTIMENT_TYPES

class SentimentAnalyzer:
    MODEL_NAME = "finiteautomata/beto-sentiment-analysis"
    CACHE_KEY = 'sentiment_analyzer'
    CACHE_TIMEOUT = 60 * 60 * 24  # 24 horas
    BATCH_SIZE = 32
    MAX_WORKERS = 4
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = self._load_model()
    
    def _load_model(self):
        try:
            # Intenta obtener del caché con lock distribuido
            with cache.lock(f"{self.CACHE_KEY}_lock", timeout=60):
                analyzer = cache.get(self.CACHE_KEY)
                if analyzer is None:
                    # Verificar memoria disponible antes de cargar
                    if self._check_memory_available():
                        analyzer = self._initialize_model()
                    else:
                        raise MemoryError("Memoria insuficiente para cargar el modelo")
                return analyzer
                
        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {str(e)}")
            raise
    
    def _check_memory_available(self):
        """Verificación más detallada de memoria disponible"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Verificar memoria RAM y SWAP
            min_required = 2 * 1024 * 1024 * 1024  # 2GB
            available = memory.available + swap.free
            
            if available < min_required:
                self.logger.warning(f"Memoria disponible baja: {available/1024/1024/1024:.2f}GB")
                
            return available >= min_required
        except Exception as e:
            self.logger.error(f"Error al verificar memoria: {str(e)}")
            return False
    
    def _initialize_model(self):
        self.logger.info("Cargando modelo de sentimientos desde cero...")
        analyzer = pipeline(
            "sentiment-analysis",
            model=self.MODEL_NAME,
            tokenizer=self.MODEL_NAME
        )
        cache.set(
            self.CACHE_KEY, 
            analyzer, 
            timeout=self.CACHE_TIMEOUT
        )
        self.logger.info("Modelo cargado y guardado en caché exitosamente")
        return analyzer
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analiza un lote de textos de forma eficiente
        """
        try:
            # Dividir en lotes más pequeños para optimizar memoria
            batches = [texts[i:i + self.BATCH_SIZE] 
                      for i in range(0, len(texts), self.BATCH_SIZE)]
            
            results = []
            start_time = time.time()
            
            for batch in batches:
                batch_results = self.analyzer(batch, truncation=True, max_length=512)
                results.extend(batch_results)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Procesados {len(texts)} textos en {processing_time:.2f} segundos")
            
            return results
        except Exception as e:
            self.logger.error(f"Error en el procesamiento por lotes: {str(e)}")
            raise
    def analyze_batch_parallel(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analiza un lote de textos usando procesamiento paralelo
        """
        def process_single(text: str) -> Dict[str, Any]:
            return self.analyzer(text, truncation=True, max_length=512)[0]
        
        try:
            start_time = time.time()
            results = []
            
            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                future_to_text = {executor.submit(process_single, text): text 
                                for text in texts}
                
                for future in as_completed(future_to_text):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        text = future_to_text[future]
                        self.logger.error(f"Error procesando texto: {text[:50]}... - Error: {str(e)}")
            
            processing_time = time.time() - start_time
            self.logger.info(f"Procesados en paralelo {len(texts)} textos en {processing_time:.2f} segundos")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en el procesamiento paralelo: {str(e)}")
            raise

    def analyze_with_cache(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Mejora en el manejo de caché y errores"""
        if not texts:
            return []
            
        try:
            results = []
            texts_to_process = []
            cache_keys = [f"sentiment_{hash(text)}" for text in texts]
            
            # Verificar caché con timeout
            with cache.lock('sentiment_cache_lock', timeout=10):
                cached_results = cache.get_many(cache_keys)
            
            for text, cache_key in zip(texts, cache_keys):
                if not text.strip():  # Ignorar textos vacíos
                    continue
                    
                if cache_key in cached_results:
                    results.append(cached_results[cache_key])
                else:
                    texts_to_process.append((text, cache_key))
            
            if texts_to_process:
                # Procesar en lotes pequeños si hay muchos textos
                if len(texts_to_process) > self.BATCH_SIZE:
                    new_results = self.analyze_batch([t[0] for t in texts_to_process])
                else:
                    new_results = self.analyze_batch_parallel([t[0] for t in texts_to_process])
                
                cache_updates = {
                    t[1]: result 
                    for t, result in zip(texts_to_process, new_results)
                }
                
                # Actualizar caché con retry
                retry_count = 3
                while retry_count > 0:
                    try:
                        cache.set_many(cache_updates, timeout=3600)
                        break
                    except Exception as e:
                        retry_count -= 1
                        if retry_count == 0:
                            self.logger.error(f"Error al actualizar caché: {str(e)}")
                
                results.extend(new_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en analyze_with_cache: {str(e)}")
            # Intentar procesar sin caché como fallback
            return self.analyze_batch(texts)
    
    