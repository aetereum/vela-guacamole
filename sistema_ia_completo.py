# sistema_ia_completo.py
import asyncio
import pandas as pd
from datetime import datetime
import yfinance as yf

class SistemaTradingIA:
    def __init__(self, capital_inicial=10000):
        self.predictor_ml = PredictorML()
        self.analizador_sentimiento = AnalizadorSentimiento()
        self.analizador_redes = AnalizadorRedesSociales()
        self.fusionador = FusionadorSeñales()
        
        # Módulos existentes
        from sistema_completo import SistemaTradingCompleto
        self.sistema_base = SistemaTradingCompleto(capital_inicial)
    
    async def analisis_avanzado_completo(self, simbolo: str) -> Dict:
        """Realiza análisis completo con IA y fusión de señales"""
        print(f"\n🧠 ANÁLISIS AVANZADO CON IA - {simbolo}")
        print("=" * 70)
        
        try:
            # 1. Obtener datos históricos
            datos = await self._obtener_datos_historicos(simbolo)
            if datos.empty:
                return {'error': 'No se pudieron obtener datos'}
            
            # 2. Análisis técnico (sistema base)
            analisis_tecnico = await self.sistema_base.sistema_trading.analizar_activo(simbolo)
            
            # 3. Predicción ML
            print("🤖 Ejecutando predicción con Machine Learning...")
            prediccion_ml = self.predictor_ml.predecir_retorno(simbolo, datos)
            
            # 4. Análisis de sentimiento
            print("📰 Analizando sentimiento de noticias...")
            sentimiento = await self.analizador_sentimiento.analizar_sentimiento_mercado(simbolo)
            
            # 5. Análisis redes sociales
            print("🌐 Analizando redes sociales...")
            redes_sociales = await self.analizador_redes.analizar_mentiones(simbolo)
            
            # 6. Fusión de todas las señales
            print("🔄 Fusionando señales...")
            señal_final = self.fusionador.generar_señal_completa(
                analisis_tecnico.get('analisis_mercado', {}),
                prediccion_ml,
                sentimiento,
                redes_sociales
            )
            
            # 7. Mostrar resultados
            self._mostrar_analisis_avanzado(
                simbolo, analisis_tecnico, prediccion_ml, 
                sentimiento, redes_sociales, señal_final
            )
            
            return {
                'simbolo': simbolo,
                'señal_final': señal_final,
                'analisis_tecnico': analisis_tecnico,
                'prediccion_ml': prediccion_ml,
                'sentimiento': sentimiento,
                'redes_sociales': redes_sociales,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Error en análisis avanzado de {simbolo}: {e}")
            return {'error': str(e)}
    
    async def _obtener_datos_historicos(self, simbolo: str) -> pd.DataFrame:
        """Obtiene datos históricos para ML"""
        try:
            ticker = yf.Ticker(simbolo)
            datos = ticker.history(period="2y")
            return datos
        except:
            return pd.DataFrame()
    
    def _mostrar_analisis_avanzado(self, simbolo: str, tecnico: Dict, ml: Dict, 
                                 sentimiento: Dict, redes: Dict, señal_final: Dict):
        """Muestra resultados del análisis avanzado"""
        print(f"\n🎯 RESULTADO FINAL FUSIONADO - {simbolo}")
        print("=" * 70)
        
        # Señal final
        decision = señal_final['decision']
        confianza = señal_final['confianza']
        color = "🟢" if decision == "COMPRAR" else "🔴" if decision == "VENDER" else "🟡"
        
        print(f"{color} DECISIÓN: {decision} (Confianza: {confianza:.1%})")
        print(f"📊 Fuerza de señal: {señal_final['fuerza_señal']:.3f}")
        
        # Desglose de señales
        print(f"\n📋 DESGLOSE DE SEÑALES:")
        for señal in señal_final['señales_individuales']:
            emoji = "🟢" if señal['direccion'] == 'ALCISTA' else "🔴" if señal['direccion'] == 'BAJISTA' else "🟡"
            print(f"   {emoji} {señal['tipo']}: {señal['direccion']} "
                  f"(Conf: {señal['confianza']:.1%}, Peso: {señal['peso']:.0%})")
        
        # ML Prediction
        if ml and 'error' not in ml:
            print(f"\n🤖 PREDICCIÓN ML:")
            print(f"   Dirección: {ml.get('direccion', 'N/A')}")
            print(f"   Retorno proyectado 5d: {ml.get('retorno_predicho_5d', 0):.2%}")
            print(f"   Confianza ML: {ml.get('confianza', 0):.1%}")
        
        # Sentimiento
        if sentimiento:
            print(f"\n📰 SENTIMIENTO NOTICIAS:")
            print(f"   Tendencia: {sentimiento.get('tendencia', 'N/A')}")
            print(f"   Noticias analizadas: {sentimiento.get('total_noticias', 0)}")
            print(f"   Confianza: {sentimiento.get('confianza', 0):.1%}")
        
        # Redes sociales
        if redes and 'error' not in redes:
            print(f"\n🌐 REDES SOCIALES:")
            print(f"   Tendencia: {redes.get('tendencia_general', 'N/A')}")
            print(f"   Volumen menciones: {redes.get('volumen_total', 0)}")
            print(f"   Engagement: {redes.get('engagement_promedio', 0):.1f}")

# EJECUCIÓN PRINCIPAL MEJORADA
async def main_avanzado():
    sistema_ia = SistemaTradingIA(capital_inicial=10000)
    
    print("🧠 SISTEMA DE TRADING CON INTELIGENCIA ARTIFICIAL")
    print("=" * 70)
    
    # Activos para análisis
    activos = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]
    
    resultados = []
    for activo in activos:
        resultado = await sistema_ia.analisis_avanzado_completo(activo)
        resultados.append(resultado)
        print("\n" + "=" * 70)
        await asyncio.sleep(2)  # Respeta límites de API
    
    # Generar resumen ejecutivo
    print("\n📊 RESUMEN EJECUTIVO:")
    print("=" * 70)
    
    for resultado in resultados:
        if 'error' not in resultado:
            señal = resultado['señal_final']
            print(f"📈 {resultado['simbolo']}: {señal['decision']} "
                  f"(Confianza: {señal['confianza']:.1%})")

if __name__ == "__main__":
    # Instalación requerida adicional:
    # pip install textblob tweepy aiohttp scikit-learn
    
    # Descargar datos para TextBlob
    import nltk
    nltk.download('punkt')
    nltk.download('brown')
    
    asyncio.run(main_avanzado())