import os
import logging
import requests
from typing import Dict, Optional

class CoinMarketCapAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.headers = {
            'X-CMC_PRO_API_KEY': api_key,
            'Accept': 'application/json'
        }
        logging.info("CoinMarketCap API initialized")

    def get_crypto_data(self, symbol: str) -> Optional[Dict]:
        """Obtiene datos detallados de una criptomoneda."""
        try:
            # Convertir símbolo a formato correcto (eliminar /USDT si está presente)
            clean_symbol = symbol.split('/')[0].upper()
            
            # Endpoint para obtener datos de la criptomoneda
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            params = {
                'symbol': clean_symbol,
                'convert': 'USD'
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if 'data' in data and clean_symbol in data['data']:
                crypto_data = data['data'][clean_symbol]
                quote = crypto_data['quote']['USD']
                
                return {
                    'id': crypto_data['id'],
                    'nombre': crypto_data['name'],
                    'simbolo': crypto_data['symbol'],
                    'precio_actual': quote['price'],
                    'volumen_24h': quote['volume_24h'],
                    'cambio_porcentual_24h': quote['percent_change_24h'],
                    'cambio_porcentual_7d': quote['percent_change_7d'],
                    'capitalizacion_mercado': quote['market_cap'],
                    'dominancia': quote['market_cap_dominance'],
                    'ultima_actualizacion': quote['last_updated']
                }
            else:
                logging.error(f"No se encontraron datos para el símbolo {clean_symbol}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error al obtener datos de CoinMarketCap: {e}")
            return None
        except KeyError as e:
            logging.error(f"Error al procesar datos de CoinMarketCap: {e}")
            return None

    def get_global_metrics(self) -> Optional[Dict]:
        """Obtiene métricas globales del mercado de criptomonedas."""
        try:
            url = f"{self.base_url}/global-metrics/quotes/latest"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                metrics = data['data']
                quote = metrics['quote']['USD']
                
                return {
                    'cryptos_activas': metrics['total_cryptocurrencies'],
                    'mercados_activos': metrics['active_market_pairs'],
                    'dominancia_btc': metrics['btc_dominance'],
                    'dominancia_eth': metrics['eth_dominance'],
                    'cap_mercado_total': quote['total_market_cap'],
                    'volumen_24h_total': quote['total_volume_24h'],
                    'ultima_actualizacion': quote['last_updated']
                }
            else:
                logging.error("No se pudieron obtener métricas globales")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error al obtener métricas globales: {e}")
            return None
        except KeyError as e:
            logging.error(f"Error al procesar métricas globales: {e}")
            return None