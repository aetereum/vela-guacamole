# CryptoMaster Panel - Sistema Avanzado de Trading 📊

Sistema profesional de análisis y trading de criptomonedas con integración de CoinMarketCap, análisis técnico avanzado, y recomendaciones de trading en tiempo real.

## 🌟 Características Principales

- ✨ Datos en tiempo real de CoinMarketCap API
- 📊 Análisis técnico avanzado con múltiples indicadores
- 🤖 Análisis de sentimiento y datos on-chain
- 💰 Gestión de riesgo profesional y cálculo de posiciones
- 📈 Recomendaciones detalladas de trading
- 🔄 Integración con múltiples fuentes de datos
- 🎯 Plan de trading personalizado por operación

## ⚙️ Instalación Paso a Paso

1. **Preparar el Entorno Python**
   ```bash
   # Instalar Python 3.11 si no está instalado
   # Descargar de: https://www.python.org/downloads/
   
   # Verificar la instalación
   python --version
   # Debe mostrar Python 3.11.x
   ```

2. **Configurar el Proyecto**
   ```bash
   # Crear y activar entorno virtual
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   
   # Instalar dependencias
   pip install Flask requests python-dotenv Pillow numpy
   ```

3. **Estructura de Archivos**
   ```
   aleatorio/
   ├── crypto_dashboard_app.py    # Aplicación principal
   ├── coinmarketcap_api.py      # Cliente de CoinMarketCap
   ├── trading_analyzer.py        # Analizador de trading
   ├── static/
   │   └── style.css             # Estilos CSS
   ├── templates/
   │   └── index.html            # Interfaz principal
   └── uploads/                   # Carpeta para uploads
   ```

4. **Configurar API Key**
   - La API key de CoinMarketCap ya está configurada
   - Key: 0a3fbf4510ec48ffa4e9d22394bb6a4a
   - No requiere configuración adicional

## 🚀 Ejecución del Sistema

1. **Iniciar el Servidor**
   ```bash
   # Activar entorno virtual si no está activado
   .\venv\Scripts\activate  # En Windows
   
   # Iniciar el servidor
   python crypto_dashboard_app.py
   ```

2. **Acceder al Dashboard**
   - Abrir el navegador
   - Ir a: http://localhost:5000
   - La interfaz debería cargarse automáticamente

3. **Realizar un Análisis**
   - Ingresar un símbolo (ej: BTC, ETH, XRP)
   - Hacer clic en "Analizar"
   - Esperar los resultados completos

## 📊 Interpretación de Resultados

1. **Panel Principal**
   - Señal principal (COMPRAR/VENDER/MANTENER)
   - Nivel de confianza de la señal
   - Explicación detallada de la decisión

2. **Datos de Mercado**
   - Precio actual
   - Volumen 24h
   - Cambios porcentuales
   - Capitalización de mercado

3. **Plan de Trading**
   - Precio de entrada óptimo
   - Stop Loss recomendado
   - Take Profit objetivo
   - Tamaño de posición sugerido

4. **Análisis Detallado**
   - Puntuación técnica
   - Análisis de sentimiento
   - Datos blockchain
   - Métricas de riesgo

## ⚠️ Notas Importantes

1. **Gestión de Riesgo**
   - Siempre usar Stop Loss
   - No exceder el 2% de riesgo por operación
   - Seguir el tamaño de posición recomendado

2. **Mantenimiento**
   - Reiniciar el servidor cada 24h
   - Verificar conexión a Internet
   - Monitorear uso de API

3. **Soporte**
   - Revisar logs en terminal
   - Verificar conexión a CoinMarketCap
   - Actualizar dependencias si necesario
- 🖼️ Análisis visual de gráficos mediante IA
- 🎯 Señales de trading con niveles de stop loss y take profit

## 📋 Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Conexión a Internet

## ⚙️ Instalación

1. **Clonar o descargar este repositorio**:
   ```bash
   cd tu/directorio/preferido
   git clone <url-del-repo>
   ```

2. **Crear y activar un entorno virtual** (opcional pero recomendado):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Uso

1. **Iniciar el servidor**:
   ```bash
   python crypto_dashboard_app.py
   ```
   O alternativamente:
   ```bash
   flask --app crypto_dashboard_app run
   ```

2. **Acceder a la aplicación**:
   - Abre tu navegador
   - Ve a: http://127.0.0.1:5000
   - La interfaz web debería cargarse automáticamente

3. **Funcionalidades principales**:
   - **Análisis por Símbolo**: 
     - Ingresa el símbolo (ej: BTC/USDT)
     - Haz clic en "Analizar"
   - **Análisis de Gráficos**:
     - Sube una imagen de un gráfico
     - El sistema analizará patrones y sentimiento

## 🔍 Guía de Uso

### Análisis por Símbolo
1. En el panel izquierdo, ingresa el símbolo de la criptomoneda
2. El sistema mostrará:
   - Señal principal de trading
   - Análisis técnico detallado
   - Indicadores ML
   - Sentimiento del mercado
   - Datos on-chain

### Análisis de Gráficos
1. En el panel derecho, sube una imagen de un gráfico
2. El sistema analizará:
   - Patrones técnicos
   - Sentimiento visual
   - Balance compradores/vendedores

## 🚨 Solución de Problemas

Si encuentras el error "No se puede acceder al sitio":

1. **Puerto 5000 ocupado**:
   ```bash
   # Intenta con puerto alternativo
   flask --app crypto_dashboard_app run -p 8080
   ```

2. **Problemas de permisos**:
   - Ejecuta como administrador en Windows
   - Usa `sudo` en Linux/Mac

3. **Otros problemas**:
   - Verifica que todas las dependencias estén instaladas
   - Asegúrate de que Python 3.11+ esté en el PATH
   - Revisa los logs en la terminal

## 📝 Notas Adicionales

- La aplicación usa modo debug por defecto para desarrollo
- Los análisis son simulados en esta versión demo
- Se recomienda usar un entorno virtual
- Los archivos se guardan en la carpeta `uploads/`

## 🤝 Contribuir

¿Encontraste un bug? ¿Tienes una sugerencia? ¡Abre un issue o envía un pull request!

Panel de control para análisis de criptomonedas con procesamiento de datos en tiempo real.

## Requisitos

```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

- `crypto_dashboard_app.py`: Aplicación principal Flask
- `master_analyzer.py`: Orquestador de análisis
- `templates/`: Plantillas HTML
- `static/`: Archivos CSS y JS
- `uploads/`: Carpeta para archivos temporales

## Ejecución

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python crypto_dashboard_app.py
   ```

3. Abrir en el navegador:
   ```
   http://localhost:5000
   ```

## Notas de Desarrollo

- La aplicación usa Flask para el servidor web
- Los análisis son simulados por defecto si faltan módulos
- Se recomienda Python 3.8+ para mejor compatibilidad