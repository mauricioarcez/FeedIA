from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any
import logging
import torch
from .decorators import check_memory

class SentimentAnalyzer:
    MODEL_NAME = "pysentimiento/robertuito-sentiment-analysis"
    _instance = None
    _analyzer = None
    _tokenizer = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            print("🔄 Creando nueva instancia de SentimentAnalyzer")
            cls._instance = super(SentimentAnalyzer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            print("🚀 Inicializando SentimentAnalyzer")
            self.logger = logging.getLogger(__name__)
            self.initialized = True
            self._load_model()
    
    def _load_model(self):
        try:
            if self._model is None:
                print("📚 Cargando modelo optimizado...")
                
                # Cargar modelo y tokenizer con configuración optimizada
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.MODEL_NAME,
                    use_fast=True  # Usar tokenizer rápido
                )
                self._model = AutoModelForSequenceClassification.from_pretrained(
                    self.MODEL_NAME,
                    torchscript=True,  # Optimizar con TorchScript
                    low_cpu_mem_usage=True
                )
                
                # Optimizaciones adicionales
                self._model.eval()  # Modo evaluación
                if torch.cuda.is_available():
                    self._model = self._model.half()  # Precisión media si hay GPU
                
                print("✅ Modelo cargado y optimizado")
            return self._model
        except Exception as e:
            print(f"❌ Error al cargar modelo: {str(e)}")
            self.logger.error(f"Error al cargar modelo: {str(e)}")
            raise

    @check_memory(min_required_gb=2)
    def analyze_with_cache(self, texts: List[str]) -> List[Dict[str, Any]]:
        if not texts:
            self.logger.warning("Lista de textos vacía")
            return []

        try:
            # Asegurar que el modelo esté cargado
            if self._model is None:
                self._load_model()

            # Mover el modelo a CPU si está disponible
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = self._model.to(device)

            inputs = self._tokenizer(
                texts, 
                padding=True, 
                truncation=True, 
                max_length=128,
                return_tensors="pt"
            ).to(device)
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                # Manejar diferentes tipos de salida del modelo
                if isinstance(outputs, tuple):
                    logits = outputs[0]
                else:
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs
                
                predictions = torch.nn.functional.softmax(logits, dim=-1)
            
            results = []
            for i, pred in enumerate(predictions):
                label = 'NEG' if pred[0] > pred[1] else 'POS'
                score = float(pred[0] if label == 'NEG' else pred[1])
                results.append({'label': label, 'score': score})
                
                self.logger.info(f"Texto analizado: {texts[i]}")
                self.logger.info(f"Resultado: {results[-1]}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis: {str(e)}", exc_info=True)
            return []
    
    