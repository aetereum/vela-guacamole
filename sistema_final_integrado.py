# sistema_final_integrado.py
import asyncio
from datetime import datetime
import pandas as pd
from typing import Dict, List

class SistemaTradingFinal:
    def __init__(self, config):
        self.config = config
        
        # Inicializar todos los módulos
        from deep_learning_predictor import DeepLearningPredictor
        from ejecucion_automatizada import EjecutorAutomatizado, GestorRiesgoAvanzado
        from order_flow_analyzer import OrderFlowAnalyzer
        from correlaciones_globales import AnalizadorCorrelaciones
        from sistema_ia_completo import SistemaTradingIA
        
        self.dl_predictor = DeepLearningPredictor()
        self.ejecutor = EjecutorAutomatizado(config)
        self.gestor_riesgo = GestorRiesgoAvanzado(config['capital_inicial'])
        self.order_flow_analyzer = OrderFlowAnalyzer()
        self.correlaciones_analyzer = AnalizadorCorrelaciones()
        self.sistema_ia = SistemaTradingIA(config['capital_inicial'])
        
        self.estado = 'INICIANDO'
        
    async def analisis_completo_integrado(self, simbolo: str) -> Dict:
        """Análisis completo integrado con todos los módulos"""
        print(f"\n🎯 ANÁLISIS INTEGRADO COMPLETO - {simbolo}")
        print("=" * 80)
        
        try:
            # 1. Análisis base con IA
            analisis_base = await self.sistema_ia.analisis_avanzado_completo(simbolo)
            
            # 2. Deep Learning Prediction
            datos_historicos = await self._obtener_datos_historicos(simbolo, "2y")
            prediccion_dl = self.dl_predictor.predecir_precio_deep_learning(simbolo, datos_historicos)
            
            # 3. Análisis de Correlaciones Globales
            correlaciones = await self.correlaciones_analyzer.analizar_correlaciones_completas(simbolo)
            
            # 4. Order Flow Analysis (simulado - necesitarías datos de nivel 2 reales)
            # order_flow = await self.order_flow_analyzer.analizar_order_flow(simbolo, datos_nivel2)
            
            # 5. Fusión Final de Todas las Señales
            señal_final = self._fusionar_todas_señales(
                analisis_base, prediccion_dl, correlaciones
            )
            
            # 6. Gestión de Riesgo Avanzada
            if 'error' not in señal_final and señal_final['decision'] in ['COMPRAR', 'VENDER']:
                gestion_riesgo = self.gestor_riesgo.calcular_tamaño_posicion_avanzado(
                    señal_final, analisis_base.get('analisis_mercado', {})
                )
                señal_final['gestion_riesgo'] = gestion_riesgo
            
            # 7. Mostrar Resultados Integrados
            self._mostrar_resultados_integrados(simbolo, señal_final, analisis_base, 
                                              prediccion_dl, correlaciones)
            
            # 8. Ejecución Automática (si está configurada)
            if (self.config.get('ejecucion_automatica', False) and 
                'gestion_riesgo' in señal_final and 
                'error' not in señal_final['gestion_riesgo']):
                
                await self._ejecutar_automaticamente(señal_final)
            
            return {
                'simbolo': simbolo,
                'señal_final': señal_final,
                'timestamp': datetime.now(),
                'estado': 'COMPLETADO'
            }
            
        except Exception as e:
            print(f"❌ Error en análisis integrado de {simbolo}: {e}")
            return {'error': str(e), 'simbolo': simbolo}
    
    def _fusionar_todas_señales(self, analisis_base: Dict, prediccion_dl: Dict, 
                              correlaciones: Dict) -> Dict:
        """Fusiona señales de todos los módulos"""
        señales = []
        
        # Señal base IA
        if 'señal_final' in analisis_base:
            señal_base = analisis_base['señal_final']
            señales.append({
                'tipo': 'IA_BASE',
                'direccion': señal_base['decision'],
                'confianza': señal_base['confianza'],
                'peso': 0.30
            })
        
        # Señal Deep Learning
        if 'error' not in prediccion_dl:
            señales.append({
                'tipo': 'DEEP_LEARNING',
                'direccion': prediccion_dl['direccion'],
                'confianza': prediccion_dl['confianza'],
                'peso': 0.25
            })
        
        # Señal Correlaciones
        if 'resumen' in correlaciones:
            resumen = correlaciones['resumen']
            if resumen.get('total_significativas', 0) > 0:
                # Usar correlación más fuerte como señal
                corr_max_pos = resumen.get('correlacion_max_positiva')
                corr_max_neg = resumen.get('correlacion_max_negativa')
                
                if corr_max_pos and corr_max_neg:
                    if abs(corr_max_pos[1]['correlacion']) > abs(corr_max_neg[1]['correlacion']):
                        señales.append({
                            'tipo': 'CORRELACIONES',
                            'direccion': 'ALCISTA',  # Correlación positiva fuerte
                            'confianza': min(abs(corr_max_pos[1]['correlacion']), 0.8),
                            'peso': 0.20
                        })
                    else:
                        señales.append({
                            'tipo': 'CORRELACIONES',
                            'direccion': 'BAJISTA',  # Correlación negativa fuerte
                            'confianza': min(abs(corr_max_neg[1]['correlacion']), 0.8),
                            'peso': 0.20
                        })
        
        # Fusión ponderada
        if not señales:
            return {'decision': 'MANTENER', 'confianza': 0.0}
        
        valores = []
        confianzas = []
        pesos = []
        
        for señal in señales:
            valor = 1 if señal['direccion'] == 'COMPRAR' else -1 if señal['direccion'] == 'VENDER' else 0
            valores.append(valor)
            confianzas.append(señal['confianza'])
            pesos.append(señal['peso'])
        
        señal_fusionada = np.average(valores, weights=[c * p for c, p in zip(confianzas, pesos)])
        confianza_total = np.average(confianzas, weights=pesos)
        
        if señal_fusionada > 0.15:
            decision = 'COMPRAR'
        elif señal_fusionada < -0.15:
            decision = 'VENDER'
        else:
            decision = 'MANTENER'
        
        return {
            'decision': decision,
            'confianza': confianza_total,
            'fuerza_señal': abs(señal_fusionada),
            'señales_individuales': señales,
            'timestamp': datetime.now()
        }
    
    async def _ejecutar_automaticamente(self, señal: Dict):
        """Ejecuta operación automáticamente"""
        if 'gestion_riesgo' not in señal or 'error' in señal['gestion_riesgo']:
            return
        
        tamaño = señal['gestion_riesgo']['tamaño_posicion']
        
        if tamaño > 0:
            print(f"🚀 EJECUTANDO ORDEN AUTOMÁTICA: {señal['decision']} {tamaño} acciones")
            await self.ejecutor.ejecutar_orden(señal, tamaño)
    
    def _mostrar_resultados_integrados(self, simbolo: str, señal_final: Dict, 
                                     analisis_base: Dict, prediccion_dl: Dict, 
                                     correlaciones: Dict):
        """Muestra resultados integrados completos"""
        print(f"\n🎯 SEÑAL FINAL INTEGRADA - {simbolo}")
        print("=" * 80)
        
        decision = señal_final['decision']
        confianza = señal_final['confianza']
        
        if decision == 'COMPRAR':
            color = "🟢"
        elif decision == 'VENDER':
            color = "🔴"
        else:
            color = "🟡"
        
        print(f"{color} DECISIÓN: {decision} (Confianza: {confianza:.1%})")
        print(f"📊 Fuerza de Señal: {señal_final['fuerza_señal']:.3f}")
        
        # Gestión de Riesgo
        if 'gestion_riesgo' in señal_final and 'error' not in señal_final['gestion_riesgo']:
            riesgo = señal_final['gestion_riesgo']
            print(f"\n⚖️ GESTIÓN DE RIESGO:")
            print(f"   Tamaño posición: {riesgo['tamaño_posicion']} acciones")
            print(f"   Stop Loss: ${riesgo['stop_loss']:.2f}")
            print(f"   Take Profit: ${riesgo['take_profit']:.2f}")
            print(f"   Riesgo: ${riesgo['riesgo_operacion']:.2f}")
            print(f"   Beneficio esperado: ${riesgo['beneficio_esperado']:.2f}")
        
        # Deep Learning
        if 'error' not in prediccion_dl:
            print(f"\n🧠 DEEP LEARNING:")
            print(f"   Precio proyectado: ${prediccion_dl['precio_predicho']:.2f}")
            print(f"   Retorno esperado: {prediccion_dl['retorno_proyectado']:.2%}")
            print(f"   Confianza DL: {prediccion_dl['confianza']:.1%}")
        
        # Correlaciones
        if 'resumen' in correlaciones:
            resumen = correlaciones['resumen']
            print(f"\n🌍 CORRELACIONES GLOBALES:")
            print(f"   Correlaciones significativas: {resumen.get('total_significativas', 0)}")
            if resumen.get('correlacion_max_positiva'):
                act, data = resumen['correlacion_max_positiva']
                print(f"   Máxima positiva: {act} ({data['correlacion']:.2f})")
            if resumen.get('correlacion_max_negativa'):
                act, data = resumen['correlacion_max_negativa']
                print(f"   Máxima negativa: {act} ({data['correlacion']:.2f})")

# CONFIGURACIÓN Y EJECUCIÓN FINAL
CONFIG_FINAL = {
    'capital_inicial': 10000,
    'broker': 'alpaca',
    'paper_trading': True,
    'alpaca_api_key': 'TU_API_KEY',
    'alpaca_secret_key': 'TU_SECRET_KEY',
    'base_url': 'https://paper-api.alpaca.markets',
    'ejecucion_automatica': False,  # Cambiar a True para ejecución automática
    'activos_monitoreo': ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL'],
    'intervalo_analisis': 30  # minutos
}

async def main_final():
    sistema_final = SistemaTradingFinal(CONFIG_FINAL)
    
    print("🚀 SISTEMA DE TRADING PROFESIONAL COMPLETO")
    print("🎯 Con Deep Learning, Ejecución Automatizada y Análisis Global")
    print("=" * 80)
    
    # Iniciar ejecutor si está configurado
    if CONFIG_FINAL.get('ejecucion_automatica', False):
        sistema_final.ejecutor.iniciar_ejecucion()
    
    # Análisis de activos
    for activo in CONFIG_FINAL['activos_monitoreo']:
        resultado = await sistema_final.analisis_completo_integrado(activo)
        
        # Esperar entre análisis para no sobrecargar APIs
        await asyncio.sleep(2)
    
    # Detener ejecutor si estaba activo
    if CONFIG_FINAL.get('ejecucion_automatica', False):
        sistema_final.ejecutor.detener_ejecucion()

if __name__ == "__main__":
    # Instalación final requerida:
    # pip install tensorflow scipy
    
    asyncio.run(main_final())