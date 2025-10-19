import numpy as np
from typing import Dict, List, Tuple, Optional

class FibonacciAnalyzer:
    def __init__(self):
        # Niveles Fibonacci clásicos
        self.fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
        # Niveles de extensión Fibonacci
        self.fib_ext = [1.272, 1.618, 2.618, 3.618]
        
    def calcular_niveles_fib(self, 
                            high: float, 
                            low: float, 
                            precio_actual: float,
                            tendencia: str) -> Dict[str, Dict[str, float]]:
        """
        Calcula niveles Fibonacci de retroceso y extensión.
        
        Args:
            high: Precio más alto del rango
            low: Precio más bajo del rango
            precio_actual: Precio actual del activo
            tendencia: 'ALCISTA' o 'BAJISTA'
        """
        range_price = high - low
        
        # Calcular niveles de retroceso
        retracements = {}
        for level in self.fib_levels:
            if tendencia == 'ALCISTA':
                price = high - (range_price * level)
            else:
                price = low + (range_price * level)
            retracements[str(level)] = round(price, 8)
            
        # Calcular niveles de extensión
        extensions = {}
        for level in self.fib_ext:
            if tendencia == 'ALCISTA':
                price = high + (range_price * (level - 1))
            else:
                price = low - (range_price * (level - 1))
            extensions[str(level)] = round(price, 8)
            
        return {
            'retracements': retracements,
            'extensions': extensions
        }
        
    def identificar_zonas_operacion(self,
                                  niveles: Dict[str, Dict[str, float]],
                                  precio_actual: float,
                                  tendencia: str) -> Dict[str, Dict[str, float]]:
        """
        Identifica zonas óptimas para entrada, stop loss y take profit.
        """
        ret = niveles['retracements']
        ext = niveles['extensions']
        
        if tendencia == 'ALCISTA':
            # En tendencia alcista
            # Buscamos entradas en retrocesos y targets en extensiones
            entrada_candidatos = [
                (level, price) for level, price in ret.items()
                if float(level) in [0.382, 0.5, 0.618] and price < precio_actual
            ]
            
            if entrada_candidatos:
                # Ordenar por nivel más cercano al precio actual
                entrada_candidatos.sort(key=lambda x: abs(float(x[1]) - precio_actual))
                entrada_nivel, entrada_precio = entrada_candidatos[0]
                
                # Stop loss debajo del siguiente nivel Fib
                stop_candidates = [
                    price for level, price in ret.items()
                    if float(level) > float(entrada_nivel)
                ]
                stop_loss = min(stop_candidates) if stop_candidates else ret['1']
                
                # Take profit en extensiones Fibonacci
                take_profit = ext['1.618']  # Objetivo conservador en 1.618
                
            else:
                # Si el precio está por debajo de todos los retrocesos
                entrada_precio = ret['0.786']  # Entrada en último retroceso
                stop_loss = ret['1']  # Stop en el mínimo
                take_profit = ext['1.272']  # Objetivo más conservador
                
        else:
            # En tendencia bajista
            # Similar pero invertido
            entrada_candidatos = [
                (level, price) for level, price in ret.items()
                if float(level) in [0.382, 0.5, 0.618] and price > precio_actual
            ]
            
            if entrada_candidatos:
                entrada_candidatos.sort(key=lambda x: abs(float(x[1]) - precio_actual))
                entrada_nivel, entrada_precio = entrada_candidatos[0]
                
                stop_candidates = [
                    price for level, price in ret.items()
                    if float(level) < float(entrada_nivel)
                ]
                stop_loss = max(stop_candidates) if stop_candidates else ret['0']
                
                take_profit = ext['1.618']
                
            else:
                entrada_precio = ret['0.786']
                stop_loss = ret['0']
                take_profit = ext['1.272']
        
        return {
            'entrada': round(float(entrada_precio), 8),
            'stop_loss': round(float(stop_loss), 8),
            'take_profit': round(float(take_profit), 8),
        }
    
    def analizar_estructura_precio(self,
                                 precios_maximos: List[float],
                                 precios_minimos: List[float],
                                 precio_actual: float) -> Tuple[str, Dict[str, float]]:
        """
        Analiza la estructura de precio para determinar tendencia y niveles Fibonacci.
        """
        if len(precios_maximos) < 2 or len(precios_minimos) < 2:
            return "NEUTRAL", {}
            
        # Identificar tendencia
        ultimo_max = max(precios_maximos[-2:])
        penultimo_max = max(precios_maximos[:-2])
        ultimo_min = min(precios_minimos[-2:])
        penultimo_min = min(precios_minimos[:-2])
        
        if ultimo_max > penultimo_max and ultimo_min > penultimo_min:
            tendencia = "ALCISTA"
            high = ultimo_max
            low = ultimo_min
        elif ultimo_max < penultimo_max and ultimo_min < penultimo_min:
            tendencia = "BAJISTA"
            high = penultimo_max
            low = ultimo_min
        else:
            tendencia = "NEUTRAL"
            return tendencia, {}
            
        # Calcular niveles Fibonacci
        niveles = self.calcular_niveles_fib(high, low, precio_actual, tendencia)
        
        # Identificar zonas de operación
        zonas = self.identificar_zonas_operacion(niveles, precio_actual, tendencia)
        
        return tendencia, {
            'niveles': niveles,
            'zonas_operacion': zonas,
            'referencia': {
                'maximo': high,
                'minimo': low
            }
        }
    
    def generar_recomendacion_fib(self,
                                 datos_mercado: Dict,
                                 analisis_tecnico: Dict) -> Dict[str, any]:
        """
        Genera una recomendación basada en análisis Fibonacci.
        """
        try:
            precio_actual = datos_mercado.get('precio_actual', 0)
            if not precio_actual:
                return {}
                
            # Obtener datos históricos (simulados para este ejemplo)
            # En una implementación real, estos vendrían de la API
            indicadores = analisis_tecnico.get('indicadores_clave', {})
            bb_superior = indicadores.get('BB_Superior', precio_actual * 1.05)
            bb_inferior = indicadores.get('BB_Inferior', precio_actual * 0.95)
            
            # Simular algunos máximos y mínimos recientes
            precios_maximos = [
                bb_superior,
                bb_superior * 0.99,
                bb_superior * 0.98
            ]
            
            precios_minimos = [
                bb_inferior,
                bb_inferior * 1.01,
                bb_inferior * 1.02
            ]
            
            # Analizar estructura de precio
            tendencia, analisis_fib = self.analizar_estructura_precio(
                precios_maximos,
                precios_minimos,
                precio_actual
            )
            
            if not analisis_fib:
                return {}
                
            # Enriquecer el análisis con información adicional
            rsi = indicadores.get('RSI', 50)
            zonas = analisis_fib['zonas_operacion']
            
            # Calidad de la señal basada en confluencia con RSI
            calidad_senal = "ALTA" if (
                (tendencia == "ALCISTA" and rsi < 40) or
                (tendencia == "BAJISTA" and rsi > 60)
            ) else "MEDIA"
            
            return {
                'tendencia_fib': tendencia,
                'calidad_senal': calidad_senal,
                'niveles_fib': analisis_fib['niveles'],
                'zonas_operacion': zonas,
                'puntos_referencia': analisis_fib['referencia'],
                'confluence_rsi': rsi
            }
            
        except Exception as e:
            print(f"Error en análisis Fibonacci: {e}")
            return {}