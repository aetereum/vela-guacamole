# rl_trader.py
import numpy as np
import pandas as pd
import asyncio
import logging
from sklearn.preprocessing import MinMaxScaler

# NOTA: Para un sistema de producción, se usarían librerías como Stable-Baselines3 y Gym.
# Esta es una implementación simplificada y simulada para demostrar la integración.

class RLTrader:
    """
    Sistema de Trading simulado con Reinforcement Learning (RL).
    En un entorno real, esto implicaría un modelo pre-entrenado (ej. PPO, A2C).
    Aquí, simulamos la decisión de un agente basado en el estado del mercado.
    """
    def __init__(self):
        self.model_cache = {}
        logging.info("RLTrader (simulado) inicializado.")

    async def predecir_accion_rl_async(self, simbolo: str, datos_actuales: pd.DataFrame) -> dict:
        """
        Predice una acción de forma asíncrona usando un modelo de RL simulado.
        """
        # En un sistema real, no se re-entrenaría en cada llamada.
        # Se cargaría un modelo pre-entrenado.
        if simbolo not in self.model_cache:
            logging.info(f"Simulando entrenamiento de modelo RL para {simbolo}...")
            await asyncio.sleep(0.5) # Simula el tiempo de carga/entrenamiento inicial
            self.model_cache[simbolo] = self._simular_entrenamiento(datos_actuales)
            logging.info(f"Modelo RL para {simbolo} listo.")

        try:
            # Extraer el estado más reciente para la predicción
            estado_actual = self._extraer_estado(datos_actuales.iloc[-1])
            
            # El "modelo" es solo un diccionario de pesos simulados
            pesos = self.model_cache[simbolo]
            
            # Calcular puntuaciones para cada acción
            score_comprar = np.dot(estado_actual, pesos['comprar'])
            score_vender = np.dot(estado_actual, pesos['vender'])
            score_mantener = np.dot(estado_actual, pesos['mantener'])

            # Decidir la acción basada en la puntuación más alta
            scores = {'COMPRAR': score_comprar, 'VENDER': score_vender, 'MANTENER': score_mantener}
            accion = max(scores, key=scores.get)
            
            # Calcular una "confianza" basada en la diferencia de puntuaciones
            sorted_scores = sorted(scores.values(), reverse=True)
            confianza = (sorted_scores[0] - sorted_scores[1]) / (sorted_scores[0] or 1)
            confianza = min(max(confianza, 0.1), 0.95) # Normalizar confianza

            return {
                'accion': accion,
                'confianza': round(confianza, 3),
                'modelo': 'RL_Simulado_v1',
                'scores': {k: round(v, 3) for k, v in scores.items()}
            }

        except Exception as e:
            logging.error(f"Error en predicción RL para {simbolo}: {e}")
            return {'error': str(e)}

    def _simular_entrenamiento(self, df: pd.DataFrame) -> dict:
        """
        Simula el resultado de un entrenamiento de RL, generando pesos para cada acción.
        Un agente real aprendería estos pesos a través de miles de iteraciones.
        """
        num_features = len(self._get_feature_names())
        
        # Generar pesos aleatorios "inteligentes"
        # Un agente de compra se fija en RSI bajo, MACD cruzando hacia arriba, etc.
        pesos_comprar = np.random.rand(num_features)
        pesos_comprar[self._get_feature_names().index('RSI')] *= -1 # Prefiere RSI bajo
        pesos_comprar[self._get_feature_names().index('MACD_diff')] *= 1 # Prefiere MACD > Signal

        # Un agente de venta se fija en lo contrario
        pesos_vender = np.random.rand(num_features)
        pesos_vender[self._get_feature_names().index('RSI')] *= 1 # Prefiere RSI alto
        pesos_vender[self._get_feature_names().index('MACD_diff')] *= -1 # Prefiere MACD < Signal

        # Un agente de mantener prefiere baja volatilidad
        pesos_mantener = np.random.rand(num_features)
        pesos_mantener[self._get_feature_names().index('BB_width')] *= -1 # Prefiere Bandas de Bollinger estrechas

        return {'comprar': pesos_comprar, 'vender': pesos_vender, 'mantener': pesos_mantener}

    def _get_feature_names(self) -> list:
        """Define las características que el agente RL observa."""
        return ['RSI', 'MACD_diff', 'ADX', 'BB_width', 'Volume_Ratio']

    def _extraer_estado(self, ultima_fila: pd.Series) -> np.ndarray:
        """
        Convierte una fila de datos del mercado en un vector de estado para el agente.
        """
        features = self._get_feature_names()
        
        # Crear la diferencia MACD si no existe
        if 'MACD_diff' not in ultima_fila:
            ultima_fila['MACD_diff'] = ultima_fila.get('MACD', 0) - ultima_fila.get('MACD_Signal', 0)

        estado = ultima_fila[features].values.astype(float)
        
        # Normalizar el estado para que el modelo funcione mejor
        # Usamos un scaler simple aquí; en producción sería más robusto
        scaler = MinMaxScaler(feature_range=(-1, 1))
        estado_normalizado = scaler.fit_transform(estado.reshape(-1, 1)).flatten()
        
        return estado_normalizado