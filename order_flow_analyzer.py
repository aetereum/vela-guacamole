# order_flow_analyzer.py
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import asyncio

class OrderFlowAnalyzer:
    def __init__(self):
        self.order_flow_data = defaultdict(list)
        self.volume_profile = defaultdict(float)
        self.large_orders = []
        
    async def analizar_order_flow(self, simbolo: str, datos_nivel2):
        """Analiza el order flow y la microestructura del mercado"""
        if not datos_nivel2:
            return {'error': 'Datos de nivel 2 no disponibles'}
        
        # Analizar presión compradora vs vendedora
        buy_pressure = self._calcular_presion_compradora(datos_nivel2)
        sell_pressure = self._calcular_presion_vendedora(datos_nivel2)
        
        # Identificar órdenes grandes
        large_orders = self._identificar_ordenes_grandes(datos_nivel2)
        
        # Analizar depth del mercado
        market_depth = self._analizar_market_depth(datos_nivel2)
        
        # Calcular imbalance
        imbalance = self._calcular_imbalance(datos_nivel2)
        
        return {
            'buy_pressure': buy_pressure,
            'sell_pressure': sell_pressure,
            'net_pressure': buy_pressure - sell_pressure,
            'large_orders_detected': len(large_orders),
            'market_depth': market_depth,
            'imbalance': imbalance,
            'timestamp': datetime.now(),
            'signal_strength': self._calcular_fuerza_señal_order_flow(buy_pressure, sell_pressure, imbalance)
        }
    
    def _calcular_presion_compradora(self, datos_nivel2):
        """Calcula la presión compradora en el order book"""
        bids = datos_nivel2.get('bids', [])
        total_bid_pressure = sum(price * size for price, size in bids[:10])  # Top 10 bids
        return total_bid_pressure
    
    def _calcular_presion_vendedora(self, datos_nivel2):
        """Calcula la presión vendedora en el order book"""
        asks = datos_nivel2.get('asks', [])
        total_ask_pressure = sum(price * size for price, size in asks[:10])  # Top 10 asks
        return total_ask_pressure
    
    def _identificar_ordenes_grandes(self, datos_nivel2, umbral=10000):
        """Identifica órdenes grandes que pueden indicar movimientos institucionales"""
        large_orders = []
        
        # Revisar bids
        for price, size in datos_nivel2.get('bids', []):
            if size * price > umbral:
                large_orders.append({
                    'type': 'BID',
                    'price': price,
                    'size': size,
                    'value': size * price
                })
        
        # Revisar asks
        for price, size in datos_nivel2.get('asks', []):
            if size * price > umbral:
                large_orders.append({
                    'type': 'ASK',
                    'price': price,
                    'size': size,
                    'value': size * price
                })
        
        return large_orders
    
    def _analizar_market_depth(self, datos_nivel2):
        """Analiza la profundidad del mercado"""
        bids = datos_nivel2.get('bids', [])
        asks = datos_nivel2.get('asks', [])
        
        depth_analysis = {
            'bid_depth': sum(size for _, size in bids),
            'ask_depth': sum(size for _, size in asks),
            'depth_ratio': sum(size for _, size in bids) / sum(size for _, size in asks) if asks else 1,
            'top_bid': bids[0][0] if bids else 0,
            'top_ask': asks[0][0] if asks else 0,
            'spread': asks[0][0] - bids[0][0] if bids and asks else 0
        }
        
        return depth_analysis
    
    def _calcular_imbalance(self, datos_nivel2):
        """Calcula el imbalance entre compras y ventas"""
        bids = datos_nivel2.get('bids', [])
        asks = datos_nivel2.get('asks', [])
        
        total_bid_volume = sum(size for _, size in bids)
        total_ask_volume = sum(size for _, size in asks)
        
        if total_bid_volume + total_ask_volume == 0:
            return 0
        
        imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        return imbalance
    
    def _calcular_fuerza_señal_order_flow(self, buy_pressure, sell_pressure, imbalance):
        """Calcula la fuerza de la señal basada en order flow"""
        net_pressure = buy_pressure - sell_pressure
        pressure_ratio = net_pressure / (buy_pressure + sell_pressure) if (buy_pressure + sell_pressure) > 0 else 0
        
        signal_strength = (pressure_ratio + imbalance) / 2
        return min(max(signal_strength, -1), 1)  # Normalizar entre -1 y 1