import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class AnalizadorMercado:
    def __init__(self):
        self.modelo = None
        self.umbral_institucional = 10000  # Volumen mínimo para considerar institucional
        
    def descargar_datos(self, simbolo, periodo="1y"):
        """Descarga datos históricos"""
        ticker = yf.Ticker(simbolo)
        datos = ticker.history(period=periodo)
        return datos
    
    def calcular_indicadores(self, datos):
        """Calcula indicadores técnicos"""
        # Medias móviles
        datos['MA20'] = datos['Close'].rolling(20).mean()
        datos['MA50'] = datos['Close'].rolling(50).mean()
        
        # RSI
        delta = datos['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        datos['RSI'] = 100 - (100 / (1 + rs))
        
        # Volumen anormal
        datos['Volumen_MA'] = datos['Volume'].rolling(20).mean()
        datos['Volumen_Anormal'] = datos['Volume'] / datos['Volumen_MA']
        
        # Detección institucional
        datos['Mov_Institucional'] = (datos['Volume'] > self.umbral_institucional) & \
                                   (datos['Close'].pct_change().abs() > 0.02)
        
        return datos.dropna()
    
    def preparar_datos_entrenamiento(self, datos):
        """Prepara datos para el modelo predictivo"""
        # Características
        caracteristicas = ['MA20', 'MA50', 'RSI', 'Volumen_Anormal', 'Mov_Institucional']
        
        # Variable objetivo: 1 si sube 2%, 0 si baja 2%, -1 si se mantiene
        datos['Target'] = 0
        retorno_futuro = datos['Close'].pct_change(5).shift(-5)  # Retorno en 5 días
        
        datos.loc[retorno_futuro > 0.02, 'Target'] = 1   # Sube
        datos.loc[retorno_futuro < -0.02, 'Target'] = -1 # Baja
        
        X = datos[caracteristicas]
        y = datos['Target']
        
        return X, y
    
    def entrenar_modelo(self, simbolo):
        """Entrena el modelo predictivo"""
        datos = self.descargar_datos(simbolo)
        datos = self.calcular_indicadores(datos)
        X, y = self.preparar_datos_entrenamiento(datos)
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        self.modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        self.modelo.fit(X_train, y_train)
        
        precision = self.modelo.score(X_test, y_test)
        print(f"Precisión del modelo: {precision:.2%}")
        
        return self.modelo
    
    def predecir_tendencia(self, simbolo):
        """Realiza predicción para el símbolo dado"""
        if self.modelo is None:
            self.entrenar_modelo(simbolo)
        
        datos = self.descargar_datos(simbolo)
        datos = self.calcular_indicadores(datos)
        
        # Últimos datos para predicción
        ultimos_datos = datos.tail(1)
        caracteristicas = ['MA20', 'MA50', 'RSI', 'Volumen_Anormal', 'Mov_Institucional']
        
        prediccion = self.modelo.predict(ultimos_datos[caracteristicas])[0]
        probabilidades = self.modelo.predict_proba(ultimos_datos[caracteristicas])[0]
        
        return prediccion, probabilidades, ultimos_datos

# Función principal de análisis
def analizar_activo(simbolo):
    analizador = AnalizadorMercado()
    
    print(f"🔍 Analizando {simbolo}...")
    prediccion, prob, datos = analizador.predecir_tendencia(simbolo)
    
    print("\n📊 ANÁLISIS COMPLETO:")
    print(f"Precio actual: ${datos['Close'].iloc[0]:.2f}")
    print(f"Volumen: {datos['Volume'].iloc[0]:,.0f}")
    print(f"RSI: {datos['RSI'].iloc[0]:.1f}")
    
    if datos['Mov_Institucional'].iloc[0]:
        print("🎯 DETECTADO: Movimiento institucional")
    
    print(f"\n🎯 PREDICCIÓN (5 días):")
    if prediccion == 1:
        print("📈 TENDENCIA: ALCISTA (+2% o más)")
    elif prediccion == -1:
        print("📉 TENDENCIA: BAJISTA (-2% o más)")
    else:
        print("➡️ TENDENCIA: LATERAL")
    
    print(f"\n📊 PROBABILIDADES:")
    print(f"Bajista: {prob[0]*100:.1f}%")
    print(f"Lateral: {prob[1]*100:.1f}%")
    print(f"Alcista: {prob[2]*100:.1f}%")

# Ejemplo de uso
if __name__ == "__main__":
    # Analizar diferentes activos
    activos = ["AAPL", "TSLA", "NVDA", "SPY"]
    
    for activo in activos:
        try:
            analizar_activo(activo)
            print("-" * 50)
        except Exception as e:
            print(f"Error analizando {activo}: {e}")