# correlaciones_globales.py
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import yfinance as yf
from datetime import datetime, timedelta
import asyncio

class AnalizadorCorrelaciones:
    def __init__(self):
        self.correlaciones = {}
        self.activos_globales = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            'IWM': 'Russell 2000',
            'EEM': 'Mercados Emergentes',
            'TLT': 'Bonos 20+ años',
            'GLD': 'Oro',
            'USO': 'Petróleo',
            'DXY': 'Dólar USD',
            'VIX': 'Volatilidad'
        }
    
    async def analizar_correlaciones_completas(self, simbolo: str, periodo: str = "6mo"):
        """Analiza correlaciones con múltiples activos globales"""
        print(f"🌍 Analizando correlaciones globales para {simbolo}...")
        
        try:
            # Obtener datos del símbolo principal
            ticker_principal = yf.Ticker(simbolo)
            datos_principal = ticker_principal.history(period=periodo)
            
            if datos_principal.empty:
                return {'error': f'No hay datos para {simbolo}'}
            
            returns_principal = datos_principal['Close'].pct_change().dropna()
            
            resultados = {}
            
            # Analizar correlación con cada activo global
            for activo, descripcion in self.activos_globales.items():
                try:
                    ticker = yf.Ticker(activo)
                    datos = ticker.history(period=periodo)
                    
                    if not datos.empty and len(datos) == len(datos_principal):
                        returns_activo = datos['Close'].pct_change().dropna()
                        
                        # Calcular correlación
                        correlacion, p_value = pearsonr(
                            returns_principal[-len(returns_activo):], 
                            returns_activo
                        )
                        
                        resultados[activo] = {
                            'descripcion': descripcion,
                            'correlacion': correlacion,
                            'p_value': p_value,
                            'significativo': p_value < 0.05,
                            'tipo': 'POSITIVA' if correlacion > 0.3 else 
                                   'NEGATIVA' if correlacion < -0.3 else 'NEUTRAL'
                        }
                        
                except Exception as e:
                    print(f"❌ Error analizando {activo}: {e}")
                    continue
            
            # Encontrar correlaciones significativas
            correlaciones_significativas = {
                k: v for k, v in resultados.items() 
                if v['significativo'] and abs(v['correlacion']) > 0.5
            }
            
            return {
                'simbolo': simbolo,
                'periodo': periodo,
                'correlaciones_completas': resultados,
                'correlaciones_significativas': correlaciones_significativas,
                'resumen': self._generar_resumen_correlaciones(correlaciones_significativas)
            }
            
        except Exception as e:
            return {'error': f'Error en análisis de correlaciones: {e}'}
    
    def _generar_resumen_correlaciones(self, correlaciones_sign: dict) -> dict:
        """Genera resumen ejecutivo de correlaciones"""
        if not correlaciones_sign:
            return {'mensaje': 'No hay correlaciones significativas'}
        
        positivas = {k: v for k, v in correlaciones_sign.items() if v['correlacion'] > 0}
        negativas = {k: v for k, v in correlaciones_sign.items() if v['correlacion'] < 0}
        
        return {
            'total_significativas': len(correlaciones_sign),
            'correlacion_max_positiva': max(positivas.items(), key=lambda x: x[1]['correlacion']) if positivas else None,
            'correlacion_max_negativa': min(negativas.items(), key=lambda x: x[1]['correlacion']) if negativas else None,
            'activos_positivos': list(positivas.keys()),
            'activos_negativos': list(negativas.keys())
        }
    
    async def predecir_impacto_evento(self, simbolo: str, evento: str):
        """Predice el impacto de eventos globales en el símbolo"""
        eventos_impacto = {
            'fed_meeting': {'impacto': -0.02, 'activos_afectados': ['SPY', 'TLT', 'DXY']},
            'cpi_data': {'impacto': -0.015, 'activos_afectados': ['SPY', 'TLT', 'DXY']},
            'earnings_season': {'impacto': 0.01, 'activos_afectados': ['SPY', 'QQQ']},
            'geopolitical_tension': {'impacto': -0.025, 'activos_afectados': ['SPY', 'GLD', 'USO']}
        }
        
        if evento not in eventos_impacto:
            return {'error': 'Evento no reconocido'}
        
        evento_info = eventos_impacto[evento]
        correlaciones = await self.analizar_correlaciones_completas(simbolo)
        
        if 'error' in correlaciones:
            return correlaciones
        
        # Calcular impacto esperado basado en correlaciones
        impacto_total = 0
        activos_afectados = 0
        
        for activo in evento_info['activos_afectados']:
            if activo in correlaciones['correlaciones_completas']:
                corr = correlaciones['correlaciones_completas'][activo]['correlacion']
                impacto_total += corr * evento_info['impacto']
                activos_afectados += 1
        
        impacto_promedio = impacto_total / max(activos_afectados, 1)
        
        return {
            'evento': evento,
            'impacto_esperado': impacto_promedio,
            'direccion_esperada': 'BAJISTA' if impacto_promedio < 0 else 'ALCISTA',
            'magnitud_esperada': abs(impacto_promedio),
            'activos_considerados': activos_afectados,
            'recomendacion': 'EVITAR' if abs(impacto_promedio) > 0.02 else 'OBSERVAR'
        }