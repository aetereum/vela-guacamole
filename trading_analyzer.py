import logging
import numpy as np
from typing import Dict, Any, Tuple, Optional
from fibonacci_analyzer import FibonacciAnalyzer

class TradingAnalyzer:
    def __init__(self):
        self.riesgo_maximo = 0.02  # 2% máximo riesgo por operación
        self.fib_analyzer = FibonacciAnalyzer()
        
    def calcular_puntuacion_tecnica(self, datos: Dict[str, Any]) -> float:
        """Calcula una puntuación técnica basada en indicadores."""
        try:
            indicadores = datos.get('analisis_tecnico_ml', {}).get('indicadores_clave', {})
            
            # Normalizar RSI (0-100)
            rsi = indicadores.get('RSI', 50)
            rsi_score = 1.0 if 40 <= rsi <= 60 else max(0, 1 - abs(rsi - 50) / 50)
            
            # Normalizar MACD
            macd = indicadores.get('MACD', 0)
            macd_signal = indicadores.get('MACD_Signal', 0)
            macd_score = 1.0 if macd > macd_signal else 0.0
            
            # Momentum
            momentum = indicadores.get('Momentum', 0)
            momentum_score = 1.0 if momentum > 0 else 0.0
            
            # Bandas de Bollinger
            bb_superior = indicadores.get('BB_Superior', 0)
            bb_inferior = indicadores.get('BB_Inferior', 0)
            precio = datos.get('datos_mercado', {}).get('precio_actual', 0)
            
            if precio and bb_superior and bb_inferior:
                if precio < bb_inferior:
                    bb_score = 1.0  # Sobrevendido
                elif precio > bb_superior:
                    bb_score = 0.0  # Sobrecomprado
                else:
                    bb_score = 0.5  # Neutral
            else:
                bb_score = 0.5
            
            # Ponderación de indicadores
            pesos = {
                'rsi': 0.3,
                'macd': 0.2,
                'momentum': 0.2,
                'bollinger': 0.3
            }
            
            puntuacion_final = (
                rsi_score * pesos['rsi'] +
                macd_score * pesos['macd'] +
                momentum_score * pesos['momentum'] +
                bb_score * pesos['bollinger']
            )
            
            return puntuacion_final
        except Exception as e:
            logging.error(f"Error en análisis técnico: {e}")
            return 0.5

    def calcular_puntuacion_sentimiento(self, datos: Dict[str, Any]) -> float:
        """Calcula una puntuación basada en análisis de sentimiento."""
        try:
            sentimiento = datos.get('analisis_sentimiento', {})
            menciones = sentimiento.get('menciones_24h', {})
            
            positivas = menciones.get('positivas', 0)
            negativas = menciones.get('negativas', 0)
            
            # Calcular ratio de sentimiento
            if positivas + negativas > 0:
                sentimiento_score = positivas / (positivas + negativas)
            else:
                sentimiento_score = 0.5
            
            return sentimiento_score
        except Exception as e:
            logging.error(f"Error en análisis de sentimiento: {e}")
            return 0.5

    def calcular_puntuacion_blockchain(self, datos: Dict[str, Any]) -> float:
        """Calcula una puntuación basada en datos on-chain."""
        try:
            blockchain = datos.get('analisis_blockchain', {})
            
            # Interpretar actividad institucional
            actividad = blockchain.get('institutional_activity', 'BAJO')
            actividad_score = {
                'ALTO': 1.0,
                'MODERADO': 0.7,
                'BAJO': 0.3
            }.get(actividad, 0.5)
            
            # Interpretar sentimiento de ballenas
            sentimiento = blockchain.get('sentiment', 'NEUTRAL')
            sentimiento_score = {
                'ACUMULACIÓN': 1.0,
                'NEUTRAL': 0.5,
                'DISTRIBUCIÓN': 0.0
            }.get(sentimiento, 0.5)
            
            return (actividad_score + sentimiento_score) / 2
        except Exception as e:
            logging.error(f"Error en análisis blockchain: {e}")
            return 0.5

    def calcular_niveles_operacion(self, 
                                 datos: Dict[str, Any], 
                                 puntuacion_global: float) -> Dict[str, float]:
        """Calcula niveles de entrada, stop loss y take profit usando Fibonacci."""
        try:
            # Obtener análisis Fibonacci
            analisis_fib = self.fib_analyzer.generar_recomendacion_fib(
                datos.get('datos_mercado', {}),
                datos.get('analisis_tecnico_ml', {})
            )
            
            if not analisis_fib:
                return self._calcular_niveles_tradicionales(datos, puntuacion_global)
            
            zonas_fib = analisis_fib.get('zonas_operacion', {})
            if not zonas_fib:
                return self._calcular_niveles_tradicionales(datos, puntuacion_global)
                
            # Ajustar niveles según la puntuación global y análisis Fibonacci
            entrada_fib = zonas_fib.get('entrada')
            stop_loss_fib = zonas_fib.get('stop_loss')
            take_profit_fib = zonas_fib.get('take_profit')
            
            if all([entrada_fib, stop_loss_fib, take_profit_fib]):
                return {
                    'entrada': round(entrada_fib, 8),
                    'stop_loss': round(stop_loss_fib, 8),
                    'take_profit': round(take_profit_fib, 8),
                    'niveles_fib': analisis_fib.get('niveles_fib', {}),
                    'calidad_senal': analisis_fib.get('calidad_senal', 'MEDIA'),
                    'tendencia_fib': analisis_fib.get('tendencia_fib', 'NEUTRAL')
                }
            else:
                return self._calcular_niveles_tradicionales(datos, puntuacion_global)
                
        except Exception as e:
            logging.error(f"Error calculando niveles Fibonacci: {e}")
            return self._calcular_niveles_tradicionales(datos, puntuacion_global)
            
    def _calcular_niveles_tradicionales(self, 
                                      datos: Dict[str, Any], 
                                      puntuacion_global: float) -> Dict[str, float]:
        """Método de respaldo para calcular niveles usando análisis tradicional."""
        try:
            precio_actual = datos.get('datos_mercado', {}).get('precio_actual', 0)
            if not precio_actual:
                return {}
            
            volatilidad = datos.get('analisis_tecnico_ml', {}).get('indicadores_clave', {}).get('ATR', 0)
            if not volatilidad:
                volatilidad = precio_actual * 0.02  # 2% por defecto
            
            # Ajustar niveles según la puntuación global
            if puntuacion_global > 0.7:  # Señal fuerte de compra
                entrada = precio_actual * 0.99  # Entrada ligeramente por debajo
                stop_loss = entrada - (volatilidad * 1.5)
                take_profit = entrada + (volatilidad * 3)
            elif puntuacion_global < 0.3:  # Señal fuerte de venta
                entrada = precio_actual * 1.01  # Entrada ligeramente por encima
                stop_loss = entrada + (volatilidad * 1.5)
                take_profit = entrada - (volatilidad * 3)
            else:  # Neutral/Hold
                entrada = precio_actual
                stop_loss = entrada - volatilidad
                take_profit = entrada + volatilidad
            
            return {
                'entrada': round(entrada, 8),
                'stop_loss': round(stop_loss, 8),
                'take_profit': round(take_profit, 8)
            }
        except Exception as e:
            logging.error(f"Error calculando niveles tradicionales: {e}")
            return {}

    def calcular_tamano_posicion(self, 
                               capital: float, 
                               precio_entrada: float, 
                               stop_loss: float) -> float:
        """Calcula el tamaño óptimo de la posición basado en gestión de riesgo."""
        try:
            if not all([capital, precio_entrada, stop_loss]):
                return 0
                
            riesgo_monetario = capital * self.riesgo_maximo
            riesgo_por_unidad = abs(precio_entrada - stop_loss)
            
            if riesgo_por_unidad == 0:
                return 0
                
            unidades = riesgo_monetario / riesgo_por_unidad
            return round(unidades, 8)
        except Exception as e:
            logging.error(f"Error calculando tamaño posición: {e}")
            return 0

    def generar_decision_trading(self, datos: Dict[str, Any], capital: float = 10000) -> Dict[str, Any]:
        """Genera una decisión completa de trading integrando todos los análisis."""
        try:
            # Calcular puntuaciones individuales
            puntuacion_tecnica = self.calcular_puntuacion_tecnica(datos)
            puntuacion_sentimiento = self.calcular_puntuacion_sentimiento(datos)
            puntuacion_blockchain = self.calcular_puntuacion_blockchain(datos)
            
            # Ponderación de las puntuaciones
            pesos = {
                'tecnico': 0.4,
                'sentimiento': 0.3,
                'blockchain': 0.3
            }
            
            puntuacion_global = (
                puntuacion_tecnica * pesos['tecnico'] +
                puntuacion_sentimiento * pesos['sentimiento'] +
                puntuacion_blockchain * pesos['blockchain']
            )
            
            # Determinar decisión
            if puntuacion_global > 0.7:
                decision = "COMPRAR"
                explicacion = "Señales alcistas fuertes en análisis técnico y fundamental"
            elif puntuacion_global < 0.3:
                decision = "VENDER"
                explicacion = "Señales bajistas dominantes en múltiples indicadores"
            else:
                decision = "MANTENER"
                explicacion = "Mercado en rango, señales mixtas"
            
            # Calcular niveles de operación
            niveles = self.calcular_niveles_operacion(datos, puntuacion_global)
            
            # Calcular tamaño de posición si hay niveles
            tamano_posicion = self.calcular_tamano_posicion(
                capital=capital,
                precio_entrada=niveles.get('entrada', 0),
                stop_loss=niveles.get('stop_loss', 0)
            ) if niveles else 0
            
            # Analizar condiciones de mercado
            mercado = datos.get('analisis_tecnico_ml', {}).get('patrones_identificados', {})
            tendencia = mercado.get('tendencia', 'NEUTRAL')
            fuerza_tendencia = mercado.get('fuerza_tendencia', 0.5)
            
            return {
                'decision': decision,
                'confianza': round(puntuacion_global * 100, 2),
                'explicacion': explicacion,
                'niveles_operacion': {
                    'entrada': niveles.get('entrada'),
                    'stop_loss': niveles.get('stop_loss'),
                    'take_profit': niveles.get('take_profit')
                },
                'gestion_riesgo': {
                    'tamano_posicion': tamano_posicion,
                    'riesgo_operacion': f"{self.riesgo_maximo * 100}%",
                    'capital_arriesgado': round(capital * self.riesgo_maximo, 2)
                },
                'analisis_detallado': {
                    'puntuacion_tecnica': round(puntuacion_tecnica * 100, 2),
                    'puntuacion_sentimiento': round(puntuacion_sentimiento * 100, 2),
                    'puntuacion_blockchain': round(puntuacion_blockchain * 100, 2),
                    'condicion_mercado': {
                        'tendencia': tendencia,
                        'fuerza': round(fuerza_tendencia * 100, 2)
                    }
                }
            }
        except Exception as e:
            logging.error(f"Error en decisión trading: {e}")
            return {
                'decision': 'MANTENER',
                'confianza': 50,
                'explicacion': 'Error en análisis, mantener posiciones actuales',
                'niveles_operacion': {},
                'gestion_riesgo': {},
                'analisis_detallado': {}
            }