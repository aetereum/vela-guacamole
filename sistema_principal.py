# sistema_completo.py
import asyncio
import schedule
import time
from datetime import datetime

class SistemaTradingCompleto:
    def __init__(self, capital_inicial=10000):
        self.sistema_trading = MiSistemaTrading(capital_inicial)
        self.backtester = BacktesterProfesional(capital_inicial)
        self.sistema_alertas = SistemaAlertas()
        self.panel_control = PanelControl(self)
        
        # Configurar alertas estándar
        configurar_alertas_estandar(self.sistema_alertas)
    
    async def ejecutar_analisis_completo(self):
        """Ejecuta análisis completo de todos los activos"""
        print(f"\n🔄 EJECUTANDO ANÁLISIS COMPLETO - {datetime.now()}")
        
        activos = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "SPY"]
        
        for activo in activos:
            try:
                # Análisis en tiempo real
                resultado = await self.sistema_trading.analizar_activo(activo)
                
                # Monitorear alertas
                if resultado and 'analisis_mercado' in resultado:
                    await self.sistema_alertas.monitorear_alertas(resultado['analisis_mercado'])
                
                await asyncio.sleep(1)  # Respetar límites de API
                
            except Exception as e:
                print(f"❌ Error en análisis de {activo}: {e}")
    
    async def ejecutar_backtesting_comparativo(self):
        """Ejecuta backtesting para comparar estrategias"""
        print(f"\n📊 EJECUTANDO BACKTESTING COMPARATIVO")
        
        activos = ["AAPL", "TSLA", "NVDA", "SPY"]
        
        for activo in activos:
            try:
                resultado = self.backtester.backtest_estrategia(activo)
                self.backtester.generar_reporte_backtesting(resultado)
                
            except Exception as e:
                print(f"❌ Error en backtesting de {activo}: {e}")
    
    def programar_tareas_automaticas(self):
        """Programa tareas automáticas del sistema"""
        # Análisis cada hora en horario de mercado
        schedule.every(60).minutes.during("09:30", "16:00").do(
            lambda: asyncio.create_task(self.ejecutar_analisis_completo())
        )
        
        # Backtesting diario después del cierre
        schedule.every().day.at("18:00").do(
            lambda: asyncio.create_task(self.ejecutar_backtesting_comparativo())
        )
        
        # Reporte matutino
        schedule.every().day.at("08:00").do(
            self.generar_reporte_matutino
        )
    
    def generar_reporte_matutino(self):
        """Genera reporte de análisis pre-mercado"""
        print(f"\n📰 REPORTE MATUTINO - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 60)
        # Aquí iría análisis de mercados globales, noticias, etc.
    
    async def ejecutar_sistema_continuo(self):
        """Ejecuta el sistema de forma continua"""
        print("🚀 INICIANDO SISTEMA DE TRADING CONTINUO")
        
        # Iniciar panel de control
        self.panel_control.iniciar_panel()
        
        # Programar tareas automáticas
        self.programar_tareas_automaticas()
        
        # Bucle principal
        while True:
            try:
                schedule.run_pending()
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Sistema detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error en bucle principal: {e}")
                await asyncio.sleep(10)

# EJECUCIÓN PRINCIPAL MEJORADA
async def main():
    # Crear sistema completo
    sistema_completo = SistemaTradingCompleto(capital_inicial=10000)
    
    # Opciones de ejecución
    print("🎯 SISTEMA DE TRADING PROFESIONAL - MENÚ PRINCIPAL")
    print("1. Análisis rápido de mercado")
    print("2. Backtesting de estrategias")
    print("3. Sistema continuo con panel web")
    print("4. Configurar alertas personalizadas")
    
    opcion = input("\nSelecciona una opción (1-4): ").strip()
    
    if opcion == "1":
        await sistema_completo.ejecutar_analisis_completo()
    
    elif opcion == "2":
        await sistema_completo.ejecutar_backtesting_comparativo()
    
    elif opcion == "3":
        await sistema_completo.ejecutar_sistema_continuo()
    
    elif opcion == "4":
        simbolo = input("Símbolo: ").strip().upper()
        print("Configura condiciones (ej: precio_subio=0.05, volumen_alto=3.0)")
        condiciones_str = input("Condiciones: ").strip()
        # Procesar condiciones...
        print("✅ Alertas configuradas")
    
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    # Instalación requerida adicional:
    # pip install flask schedule
    
    asyncio.run(main())