# ejecucion_automatizada.py
import asyncio
import time
from datetime import datetime
from typing import Dict, List
import hmac
import hashlib
import base64
import aiohttp
import json

class EjecutorAutomatizado:
    def __init__(self, config):
        self.config = config
        self.ordenes_activas = []
        self.estado = 'DETENIDO'
        
    async conectar_api(self, broker: str):
        """Conecta con la API del broker"""
        if broker == 'alpaca':
            return await self._conectar_alpaca()
        elif broker == 'ibkr':
            return await self._conectar_ibkr()
        else:
            raise ValueError(f"Broker no soportado: {broker}")
    
    async def _conectar_alpaca(self):
        """Conecta con Alpaca Markets API"""
        base_url = "https://paper-api.alpaca.markets" if self.config['paper_trading'] else "https://api.alpaca.markets"
        
        headers = {
            'APCA-API-KEY-ID': self.config['alpaca_api_key'],
            'APCA-API-SECRET-KEY': self.config['alpaca_secret_key']
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Verificar conexión
            async with session.get(f"{base_url}/v2/account") as response:
                if response.status == 200:
                    account_data = await response.json()
                    print(f"✅ Conectado a Alpaca - Cuenta: {account_data['account_number']}")
                    return session
                else:
                    raise ConnectionError("Error conectando a Alpaca")
    
    async def ejecutar_orden(self, señal: Dict, tamaño_posicion: int):
        """Ejecuta orden automáticamente basada en señal"""
        if self.estado != 'ACTIVO':
            print("❌ Ejecutor no activo")
            return
        
        simbolo = señal['simbolo']
        accion = señal['decision']
        precio_actual = señal.get('precio_actual', 0)
        
        if accion not in ['COMPRAR', 'VENDER']:
            print(f"❌ Acción no válida: {accion}")
            return
        
        try:
            # Conectar con broker
            session = await self.conectar_api(self.config['broker'])
            
            # Preparar orden
            orden = {
                'symbol': simbolo,
                'qty': tamaño_posicion,
                'side': 'buy' if accion == 'COMPRAR' else 'sell',
                'type': 'market',
                'time_in_force': 'gtc'
            }
            
            # Enviar orden
            async with session.post(f"{self.config['base_url']}/v2/orders", json=orden) as response:
                if response.status == 200:
                    orden_data = await response.json()
                    print(f"✅ Orden ejecutada - {accion} {tamaño_posicion} {simbolo}")
                    
                    # Registrar orden
                    self._registrar_orden(orden_data, señal)
                    
                    return orden_data
                else:
                    error_text = await response.text()
                    print(f"❌ Error ejecutando orden: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error en ejecución automática: {e}")
    
    def _registrar_orden(self, orden_data: Dict, señal: Dict):
        """Registra orden en base de datos"""
        orden_info = {
            'id_orden': orden_data['id'],
            'simbolo': orden_data['symbol'],
            'accion': orden_data['side'],
            'cantidad': orden_data['qty'],
            'precio_ejecucion': orden_data.get('filled_avg_price', 0),
            'estado': orden_data['status'],
            'timestamp': datetime.now(),
            'señal_origen': señal
        }
        
        self.ordenes_activas.append(orden_info)
        
        # Guardar en base de datos
        self._guardar_orden_db(orden_info)
    
    def _guardar_orden_db(self, orden_info: Dict):
        """Guarda orden en base de datos"""
        try:
            import sqlite3
            conn = sqlite3.connect('trading_db.sqlite')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ordenes_ejecutadas 
                (id_orden, simbolo, accion, cantidad, precio, estado, timestamp, señal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                orden_info['id_orden'],
                orden_info['simbolo'],
                orden_info['accion'],
                orden_info['cantidad'],
                orden_info['precio_ejecucion'],
                orden_info['estado'],
                orden_info['timestamp'],
                json.dumps(orden_info['señal_origen'])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error guardando orden en DB: {e}")
    
    async def monitorear_ordenes(self):
        """Monitorea órdenes activas"""
        while self.estado == 'ACTIVO':
            try:
                session = await self.conectar_api(self.config['broker'])
                
                for orden in self.ordenes_activas[:]:  # Copia para modificar durante iteración
                    if orden['estado'] in ['new', 'partially_filled']:
                        # Verificar estado actual
                        async with session.get(f"{self.config['base_url']}/v2/orders/{orden['id_orden']}") as response:
                            if response.status == 200:
                                orden_actual = await response.json()
                                orden['estado'] = orden_actual['status']
                                orden['precio_ejecucion'] = orden_actual.get('filled_avg_price', 0)
                                
                                if orden_actual['status'] == 'filled':
                                    print(f"✅ Orden completada - {orden['simbolo']}")
                                    # Ejecutar acciones post-orden si es necesario
                                    await self._procesar_orden_completada(orden)
                
                await asyncio.sleep(10)  # Verificar cada 10 segundos
                
            except Exception as e:
                print(f"❌ Error monitoreando órdenes: {e}")
                await asyncio.sleep(30)
    
    async def _procesar_orden_completada(self, orden: Dict):
        """Procesa orden completada (stop loss, take profit)"""
        # Aquí se pueden configurar órdenes OCO (One-Cancels-Other)
        # para stop loss y take profit automáticos
        pass
    
    def iniciar_ejecucion(self):
        """Inicia el sistema de ejecución automática"""
        self.estado = 'ACTIVO'
        print("🚀 Sistema de ejecución automática INICIADO")
        
        # Iniciar monitoreo en segundo plano
        asyncio.create_task(self.monitorear_ordenes())
    
    def detener_ejecucion(self):
        """Detiene el sistema de ejecución automática"""
        self.estado = 'DETENIDO'
        print("🛑 Sistema de ejecución automática DETENIDO")

class GestorRiesgoAvanzado:
    def __init__(self, capital_total: float):
        self.capital_total = capital_total
        self.operaciones_activas = []
        self.max_operaciones_simultaneas = 5
        self.riesgo_diario_maximo = 0.05  # 5% del capital diario
        self.riesgo_acumulado_hoy = 0.0
        
    def calcular_tamaño_posicion_avanzado(self, señal: Dict, datos_mercado: Dict) -> Dict:
        """Calcula tamaño de posición con gestión de riesgo avanzada"""
        precio_actual = datos_mercado.get('precio_actual', 0)
        volatilidad = datos_mercado.get('volatilidad', 0.02)
        confianza = señal.get('confianza', 0.5)
        
        # Riesgo base por operación
        riesgo_base = self.capital_total * 0.02  # 2% base
        
        # Ajustar por confianza
        riesgo_ajustado = riesgo_base * confianza
        
        # Ajustar por volatilidad
        if volatilidad > 0.05:  # Alta volatilidad
            riesgo_ajustado *= 0.5
        elif volatilidad < 0.01:  # Baja volatilidad
            riesgo_ajustado *= 1.2
        
        # Verificar límite diario
        riesgo_disponible = (self.capital_total * self.riesgo_diario_maximo) - self.riesgo_acumulado_hoy
        riesgo_final = min(riesgo_ajustado, riesgo_disponible)
        
        if riesgo_final <= 0:
            return {'error': 'Límite de riesgo diario alcanzado'}
        
        # Calcular stop loss dinámico
        stop_loss = self._calcular_stop_loss_dinamico(precio_actual, volatilidad, señal['decision'])
        
        # Calcular tamaño de posición
        perdida_por_unidad = abs(precio_actual - stop_loss)
        if perdida_por_unidad == 0:
            return {'error': 'Stop loss inválido'}
        
        tamaño_posicion = riesgo_final / perdida_por_unidad
        
        # Asegurar que no exceda el 10% del capital
        inversion_maxima = self.capital_total * 0.10
        tamaño_maximo = inversion_maxima / precio_actual
        tamaño_posicion = min(tamaño_posicion, tamaño_maximo)
        
        # Calcular take profit con ratio riesgo/beneficio
        take_profit = self._calcular_take_profit(precio_actual, stop_loss, señal['decision'])
        
        return {
            'tamaño_posicion': int(tamaño_posicion),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'riesgo_operacion': riesgo_final,
            'beneficio_esperado': riesgo_final * 2,  # Ratio 1:2
            'ratio_riesgo_beneficio': 2.0
        }
    
    def _calcular_stop_loss_dinamico(self, precio: float, volatilidad: float, direccion: str) -> float:
        """Calcula stop loss dinámico basado en volatilidad"""
        atr_multiplier = 2.0  # 2 ATRs
        
        if direccion == 'COMPRAR':
            return precio * (1 - (volatilidad * atr_multiplier))
        else:  # VENDER
            return precio * (1 + (volatilidad * atr_multiplier))
    
    def _calcular_take_profit(self, precio: float, stop_loss: float, direccion: str) -> float:
        """Calcula take profit con ratio 1:2"""
        distancia_riesgo = abs(precio - stop_loss)
        
        if direccion == 'COMPRAR':
            return precio + (distancia_riesgo * 2)
        else:  # VENDER
            return precio - (distancia_riesgo * 2)
    
    def registrar_operacion(self, operacion: Dict):
        """Registra nueva operación en el gestor de riesgo"""
        self.operaciones_activas.append(operacion)
        self.riesgo_acumulado_hoy += operacion['riesgo_operacion']
        
        # Reiniciar riesgo diario al nuevo día
        if datetime.now().hour == 0 and datetime.now().minute == 0:
            self.riesgo_acumulado_hoy = 0.0