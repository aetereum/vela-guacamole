# alertas_tiempo_real.py
import asyncio
import smtplib
from email.mime.text import MimeText
import time
from datetime import datetime

class SistemaAlertas:
    def __init__(self):
        self.alertas_activas = []
        self.umbrales = {
            'volumen': 2.0,
            'precio': 0.03,  # 3%
            'rsi_sobrecompra': 70,
            'rsi_sobreventa': 30
        }
    
    def configurar_alertas_personalizadas(self, simbolo: str, condiciones: Dict):
        """Configura alertas personalizadas para un símbolo"""
        alerta_id = f"{simbolo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alerta = {
            'id': alerta_id,
            'simbolo': simbolo,
            'condiciones': condiciones,
            'activa': True,
            'creada': datetime.now(),
            'disparada': False
        }
        
        self.alertas_activas.append(alerta)
        print(f"✅ Alerta configurada para {simbolo}: {condiciones}")
        return alerta_id
    
    async def monitorear_alertas(self, datos_mercado: Dict):
        """Monitorea condiciones de alertas en tiempo real"""
        for alerta in self.alertas_activas:
            if not alerta['activa'] or alerta['disparada']:
                continue
            
            simbolo = alerta['simbolo']
            if simbolo != datos_mercado.get('simbolo'):
                continue
            
            if self._verificar_condiciones(alerta['condiciones'], datos_mercado):
                await self._disparar_alerta(alerta, datos_mercado)
                alerta['disparada'] = True
    
    def _verificar_condiciones(self, condiciones: Dict, datos: Dict) -> bool:
        """Verifica si se cumplen las condiciones de alerta"""
        for condicion, valor in condiciones.items():
            if condicion == 'precio_subio' and datos.get('cambio_porcentual', 0) < valor:
                return False
            elif condicion == 'precio_bajo' and datos.get('cambio_porcentual', 0) > -valor:
                return False
            elif condicion == 'volumen_alto' and datos.get('volumen_ratio', 1) < valor:
                return False
            elif condicion == 'rsi_sobrecompra' and datos.get('rsi', 50) < valor:
                return False
            elif condicion == 'rsi_sobreventa' and datos.get('rsi', 50) > valor:
                return False
        return True
    
    async def _disparar_alerta(self, alerta: Dict, datos: Dict):
        """Dispara una alerta cuando se cumplen las condiciones"""
        mensaje = self._construir_mensaje_alerta(alerta, datos)
        
        # Mostrar en consola
        print(f"🚨 ALERTA DISPARADA: {mensaje}")
        
        # Enviar por email (opcional)
        await self._enviar_email_alerta(mensaje)
        
        # Guardar en base de datos
        self._guardar_alerta_db(alerta, datos, mensaje)
    
    def _construir_mensaje_alerta(self, alerta: Dict, datos: Dict) -> str:
        """Construye mensaje de alerta"""
        simbolo = alerta['simbolo']
        precio = datos.get('precio_actual', 0)
        cambio = datos.get('cambio_porcentual', 0)
        volumen = datos.get('volumen_ratio', 1)
        rsi = datos.get('rsi', 50)
        
        return (f"ALERTA {simbolo}\n"
                f"Precio: ${precio:.2f} ({cambio:+.2f}%)\n"
                f"Volumen: {volumen:.1f}x normal\n"
                f"RSI: {rsi:.1f}\n"
                f"Condiciones: {alerta['condiciones']}\n"
                f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def _enviar_email_alerta(self, mensaje: str):
        """Envía alerta por email (configurar primero)"""
        try:
            # Configuración de email (completar con tus datos)
            email_config = {
                'smtp_server': 'smtp.gmail.com',
                'port': 587,
                'sender_email': 'tu_email@gmail.com',
                'password': 'tu_password',
                'receiver_email': 'destino@gmail.com'
            }
            
            # Solo enviar si está configurado
            if email_config['sender_email'] != 'tu_email@gmail.com':
                msg = MimeText(mensaje)
                msg['Subject'] = '🚨 Alerta de Trading'
                msg['From'] = email_config['sender_email']
                msg['To'] = email_config['receiver_email']
                
                with smtplib.SMTP(email_config['smtp_server'], email_config['port']) as server:
                    server.starttls()
                    server.login(email_config['sender_email'], email_config['password'])
                    server.send_message(msg)
                
                print("✅ Alerta enviada por email")
                
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
    
    def _guardar_alerta_db(self, alerta: Dict, datos: Dict, mensaje: str):
        """Guarda alerta en base de datos"""
        try:
            conn = sqlite3.connect('trading_db.sqlite')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alertas (simbolo, condiciones, mensaje, precio, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (alerta['simbolo'], str(alerta['condiciones']), mensaje, 
                  datos.get('precio_actual', 0), datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error guardando alerta en DB: {e}")

# Configuración de alertas comunes
def configurar_alertas_estandar(sistema_alertas: SistemaAlertas):
    """Configura alertas estándar para los principales activos"""
    activos = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
    
    for activo in activos:
        # Alerta de volumen anormal
        sistema_alertas.configurar_alertas_personalizadas(activo, {
            'volumen_alto': 3.0  # 3x volumen normal
        })
        
        # Alerta de movimiento de precio
        sistema_alertas.configurar_alertas_personalizadas(activo, {
            'precio_subio': 0.05,  # 5% de subida
            'precio_bajo': 0.05    # 5% de bajada
        })
        
        # Alerta RSI extremos
        sistema_alertas.configurar_alertas_personalizadas(activo, {
            'rsi_sobrecompra': 75,
            'rsi_sobreventa': 25
        })