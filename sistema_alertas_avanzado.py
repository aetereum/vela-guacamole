# sistema_alertas_avanzado.py
import asyncio
from datetime import datetime, timedelta
import aiohttp
import json
from typing import Dict, List
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

class SistemaAlertasAvanzado:
    """Sistema avanzado de alertas multi-plataforma"""
    
    def __init__(self, config):
        self.config = config
        self.alertas_activas = []
        self.historial_alertas = []
        
        # Configuración de servicios externos
        self.pushover_config = config.get('pushover', {})
        self.telegram_config = config.get('telegram', {})
        self.email_config = config.get('email', {})
    
    async def configurar_alerta_personalizada(self, simbolo: str, condiciones: Dict, 
                                            canales: List[str] = ['email']):
        """Configurar alerta personalizada avanzada"""
        alerta_id = f"{simbolo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alerta = {
            'id': alerta_id,
            'simbolo': simbolo,
            'condiciones': condiciones,
            'canales': canales,
            'activa': True,
            'disparada': False,
            'timestamp_creacion': datetime.now(),
            'timestamp_disparo': None
        }
        
        self.alertas_activas.append(alerta)
        
        print(f"✅ Alerta configurada: {simbolo} - {condiciones}")
        return alerta_id
    
    async def monitorear_alertas_en_tiempo_real(self, datos_mercado: Dict):
        """Monitoreo en tiempo real de condiciones de alerta"""
        for alerta in self.alertas_activas:
            if not alerta['activa'] or alerta['disparada']:
                continue
            
            if alerta['simbolo'] != datos_mercado.get('simbolo'):
                continue
            
            if self._evaluar_condiciones_complejas(alerta['condiciones'], datos_mercado):
                await self._disparar_alerta_multicanal(alerta, datos_mercado)
                alerta['disparada'] = True
                alerta['timestamp_disparo'] = datetime.now()
    
    def _evaluar_condiciones_complejas(self, condiciones: Dict, datos: Dict) -> bool:
        """Evaluar condiciones complejas de alerta"""
        for condicion, valor in condiciones.items():
            if condicion == 'precio_por_encima' and datos.get('precio_actual', 0) <= valor:
                return False
            elif condicion == 'precio_por_debajo' and datos.get('precio_actual', 0) >= valor:
                return False
            elif condicion == 'volumen_anormal' and datos.get('volumen_ratio', 1) < valor:
                return False
            elif condicion == 'rsi_sobrecompra' and datos.get('rsi', 50) < valor:
                return False
            elif condicion == 'rsi_sobreventa' and datos.get('rsi', 50) > valor:
                return False
            elif condicion == 'cambio_porcentual' and abs(datos.get('cambio_porcentual', 0)) < valor:
                return False
            elif condicion == 'patron_tecnico' and not self._detectar_patron_tecnico(valor, datos):
                return False
        
        return True
    
    def _detectar_patron_tecnico(self, patron: str, datos: Dict) -> bool:
        """Detectar patrones técnicos específicos"""
        # Implementación simplificada de detección de patrones
        if patron == 'double_top' and datos.get('precio_actual', 0) < datos.get('resistencia', 0) * 0.98:
            return True
        elif patron == 'double_bottom' and datos.get('precio_actual', 0) > datos.get('soporte', 0) * 1.02:
            return True
        elif patron == 'head_shoulders':
            # Lógica simplificada para head & shoulders
            return datos.get('rsi', 50) > 70 and datos.get('precio_actual', 0) < datos.get('precio_max_50d', 0)
        
        return False
    
    async def _disparar_alerta_multicanal(self, alerta: Dict, datos: Dict):
        """Disparar alerta a través de múltiples canales"""
        mensaje = self._construir_mensaje_alerta_avanzado(alerta, datos)
        
        print(f"🚨 ALERTA DISPARADA: {mensaje}")
        
        # Enviar a través de canales configurados
        for canal in alerta['canales']:
            try:
                if canal == 'email':
                    await self._enviar_email_alerta(mensaje)
                elif canal == 'pushover':
                    await self._enviar_push_notification(mensaje)
                elif canal == 'telegram':
                    await self._enviar_telegram_message(mensaje)
                elif canal == 'webhook':
                    await self._enviar_webhook(alerta, datos)
                
                print(f"✅ Alerta enviada por {canal}")
                
            except Exception as e:
                print(f"❌ Error enviando alerta por {canal}: {e}")
        
        # Registrar en historial
        self._registrar_alerta_historial(alerta, datos, mensaje)
    
    def _construir_mensaje_alerta_avanzado(self, alerta: Dict, datos: Dict) -> str:
        """Construir mensaje de alerta avanzado"""
        simbolo = alerta['simbolo']
        precio = datos.get('precio_actual', 0)
        cambio = datos.get('cambio_porcentual', 0)
        volumen = datos.get('volumen_ratio', 1)
        rsi = datos.get('rsi', 50)
        
        mensaje = f"""
🚨 ALERTA DE TRADING - {simbolo}

📊 DATOS ACTUALES:
• Precio: ${precio:.2f} ({cambio:+.2f}%)
• Volumen: {volumen:.1f}x normal
• RSI: {rsi:.1f}
• Condición: {alerta['condiciones']}

⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 ACCIÓN RECOMENDADA:
{self._generar_recomendacion_accion(alerta['condiciones'], datos)}
"""
        return mensaje.strip()
    
    def _generar_recomendacion_accion(self, condiciones: Dict, datos: Dict) -> str:
        """Generar recomendación de acción basada en condiciones"""
        if 'rsi_sobrecompra' in condiciones:
            return "Considerar tomar ganancias o establecer stop loss"
        elif 'rsi_sobreventa' in condiciones:
            return "Posible oportunidad de compra en zona de sobreventa"
        elif 'volumen_anormal' in condiciones:
            return "Movimiento institucional detectado - monitorear de cerca"
        elif 'patron_tecnico' in condiciones:
            return "Patrón técnico completado - preparar operación"
        else:
            return "Revisar análisis completo para decisión"
    
    async def _enviar_push_notification(self, mensaje: str):
        """Enviar notificación push via Pushover"""
        if not self.pushover_config:
            return
        
        data = {
            'token': self.pushover_config.get('api_token'),
            'user': self.pushover_config.get('user_key'),
            'message': mensaje,
            'title': '🚨 Alerta de Trading',
            'priority': 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.pushover.net/1/messages.json', data=data) as response:
                if response.status != 200:
                    print(f"❌ Error Pushover: {await response.text()}")
    
    async def _enviar_telegram_message(self, mensaje: str):
        """Enviar mensaje via Telegram"""
        if not self.telegram_config:
            return
        
        bot_token = self.telegram_config.get('bot_token')
        chat_id = self.telegram_config.get('chat_id')
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': mensaje,
            'parse_mode': 'HTML'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    print(f"❌ Error Telegram: {await response.text()}")
    
    async def _enviar_webhook(self, alerta: Dict, datos: Dict):
        """Enviar alerta via webhook"""
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            return
        
        payload = {
            'alerta': alerta,
            'datos': datos,
            'timestamp': datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status not in [200, 201]:
                    print(f"❌ Error webhook: {await response.text()}")
    
    def _registrar_alerta_historial(self, alerta: Dict, datos: Dict, mensaje: str):
        """Registrar alerta en historial"""
        registro = {
            'alerta_id': alerta['id'],
            'simbolo': alerta['simbolo'],
            'condiciones': alerta['condiciones'],
            'mensaje': mensaje,
            'datos_mercado': datos,
            'timestamp': datetime.now()
        }
        
        self.historial_alertas.append(registro)
        
        # Mantener solo últimos 1000 registros
        if len(self.historial_alertas) > 1000:
            self.historial_alertas = self.historial_alertas[-1000:]
    
    async def _enviar_email_alerta(self, mensaje: str):
        """Enviar alerta por email"""