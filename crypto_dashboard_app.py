# crypto_dashboard_app.py
import os
import sys
import asyncio
import logging
import json
import datetime
import time
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
from coinmarketcap_api import CoinMarketCapAPI
from trading_analyzer import TradingAnalyzer
from threading import Thread

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, bool):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configurar API de CoinMarketCap y Analizador de Trading
CMC_API_KEY = '0a3fbf4510ec48ffa4e9d22394bb6a4a'
cmc_api = CoinMarketCapAPI(CMC_API_KEY)
trading_analyzer = TradingAnalyzer()

# Intentamos importar el orquestador maestro; si no existe, creamos un stub mínimo
try:
    from master_analyzer import CryptoMasterAnalyzer
except Exception:
    CryptoMasterAnalyzer = None

# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Inicializar el analizador maestro una vez (puede dar None si falla)
master_analyzer = None
if CryptoMasterAnalyzer:
    try:
        master_analyzer = CryptoMasterAnalyzer()
        logging.info("CryptoMasterAnalyzer inicializado correctamente.")
    except Exception as e:
        logging.error(f"Error al inicializar CryptoMasterAnalyzer: {e}")
        master_analyzer = None
else:
    logging.warning("No se encontró master_analyzer; algunas rutas usarán respuestas simuladas.")

def generate_realtime_data(symbol):
    while True:
        try:
            # Obtener datos actualizados
            cmc_data = cmc_api.get_crypto_data(symbol)
            if cmc_data:
                data = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'precio': float(cmc_data['precio_actual']),
                    'volumen_24h': float(cmc_data['volumen_24h']),
                    'cambio_24h': float(cmc_data['cambio_porcentual_24h']),
                }
                
                if master_analyzer:
                    analysis = asyncio.run(master_analyzer.analisis_rapido(symbol))
                    if analysis:
                        data.update(analysis)
                
                yield f"data: {json.dumps(data)}\n\n"
            
        except Exception as e:
            logging.error(f"Error en stream de datos: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        time.sleep(5)  # Actualizar cada 5 segundos

@app.route('/stream/<symbol>')
def stream(symbol):
    return Response(generate_realtime_data(symbol),
                   mimetype='text/event-stream',
                   headers={'Cache-Control': 'no-cache',
                           'Connection': 'keep-alive'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if not master_analyzer:
        return jsonify({'error': 'El servidor de análisis no está disponible.'}), 500

    symbol = request.form.get('symbol')
    if not symbol:
        return jsonify({'error': 'El símbolo es obligatorio.'}), 400

    logging.info(f"Iniciando análisis para el símbolo: {symbol}")
    try:
        # Obtener datos de CoinMarketCap
        cmc_data = cmc_api.get_crypto_data(symbol)
        datos_mercado = None
        if cmc_data:
            datos_mercado = {
                'simbolo': cmc_data['simbolo'],
                'precio_actual': float(cmc_data['precio_actual']),
                'volumen_24h': float(cmc_data['volumen_24h']),
                'cambio_24h': float(cmc_data['cambio_porcentual_24h']),
                'cambio_7d': float(cmc_data['cambio_porcentual_7d']),
                'capitalizacion': float(cmc_data['capitalizacion_mercado']),
                'dominancia': float(cmc_data['dominancia'])
            }

        # Obtener métricas globales
        global_metrics = cmc_api.get_global_metrics()
        if global_metrics:
            global_metrics = {k: float(v) if isinstance(v, (int, float)) else v 
                            for k, v in global_metrics.items()}

        # Realizar análisis técnico y de sentimiento
        analysis_result = None
        if master_analyzer:
            try:
                analysis_result = asyncio.run(master_analyzer.analisis_completo_integrado(symbol))
            except Exception as e:
                logging.error(f"Error en análisis técnico: {e}")
                analysis_result = {}

        # Integrar todos los datos
        combined_result = {
            'simbolo': symbol.upper(),
            'datos_mercado': datos_mercado if datos_mercado else {},
            'metricas_globales': global_metrics if global_metrics else {},
            'señal_final': {
                'decision': 'NEUTRAL',
                'confianza_final': 0.5
            }
        }

        # Integrar datos y generar análisis avanzado
        initial_result = {
            'simbolo': symbol.upper(),
            'datos_mercado': datos_mercado if datos_mercado else {},
            'metricas_globales': global_metrics if global_metrics else {}
        }

        # Si hay resultados del análisis técnico, integrarlos
        if analysis_result and isinstance(analysis_result, dict):
            initial_result.update(analysis_result)

        # Generar decisión de trading avanzada
        decision_trading = trading_analyzer.generar_decision_trading(
            initial_result,
            capital=10000  # Capital base para cálculos
        )

        # Combinar todo en el resultado final
        combined_result = {
            **initial_result,
            'señal_final': {
                'decision': decision_trading['decision'],
                'confianza_final': decision_trading['confianza'] / 100,
                'explicacion': decision_trading['explicacion']
            },
            'recomendacion_trading': {
                'niveles': decision_trading['niveles_operacion'],
                'gestion_riesgo': decision_trading['gestion_riesgo'],
                'analisis_detallado': decision_trading['analisis_detallado']
            }
        }

        return jsonify(combined_result)
    except Exception as e:
        logging.error(f"Excepción en /analyze para {symbol}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    if 'chart_image' not in request.files:
        return jsonify({'error': 'No se encontró el archivo de imagen.'}), 400

    file = request.files['chart_image']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(filepath)
        logging.info(f"Imagen '{filename}' guardada en '{filepath}'")
        if master_analyzer:
            image_analysis = master_analyzer.analizar_imagen_simulado(filepath)
            return jsonify(image_analysis)
        else:
            # Respuesta simulada si no hay analizador
            return jsonify({'analisis_visual': 'NEUTRAL', 'confianza_visual': 0.5, 'compradores_vs_vendedores': '0 vs 0'})
    except Exception as e:
        logging.error(f"Error al procesar imagen: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        print("Iniciando servidor en http://localhost:5000")
        app.run(host='localhost', port=5000, debug=True, use_reloader=False)
    except OSError as e:
        print(f"Error en puerto 5000: {e}")
        print("Intentando puerto alternativo 8080...")
        app.run(host='localhost', port=8080, debug=True, use_reloader=False)