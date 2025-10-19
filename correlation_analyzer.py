# correlation_analyzer.py
import pandas as pd
import numpy as np
import ccxt.async_support as ccxt
import asyncio
import logging

class CorrelationAnalyzer:
    """
    Analiza las correlaciones de una criptomoneda con activos clave del mercado.
    """
    def __init__(self):
        # Activos de referencia para correlación
        self.benchmark_assets = {
            'BTC/USDT': 'Bitcoin',
            'ETH/USDT': 'Ethereum',
            # En un sistema de producción, se podrían añadir futuros del S&P 500, Oro, etc.
            # desde un proveedor de datos de mercado tradicional.
        }
        self.exchange = ccxt.binance({'enableRateLimit': True})
        logging.info("CorrelationAnalyzer inicializado.")

    async def close_connections(self):
        await self.exchange.close()

    async def get_returns(self, symbol, days=90):
        """Obtiene los retornos diarios de un símbolo."""
        try:
            # timeframe '1d' para retornos diarios
            ohlcv = await self.exchange.fetch_ohlcv(symbol, '1d', limit=days)
            if not ohlcv:
                return pd.Series(dtype=np.float64)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df['close'].pct_change().dropna()
        except Exception as e:
            logging.warning(f"No se pudieron obtener datos para correlación de {symbol}: {e}")
            return pd.Series(dtype=np.float64)

    async def analyze_correlations(self, main_symbol: str, days: int = 90) -> dict:
        """
        Analiza las correlaciones de un símbolo principal contra los activos de referencia.
        """
        logging.info(f"Iniciando análisis de correlación para {main_symbol}")
        main_returns = await self.get_returns(main_symbol, days)

        if main_returns.empty:
            return {'error': f'No se pudieron obtener datos para {main_symbol}'}

        correlation_results = {}
        
        # Crear una lista de benchmarks a consultar (excluyendo el símbolo principal)
        benchmarks_to_fetch = {s: n for s, n in self.benchmark_assets.items() if s != main_symbol}
        
        # Crear tareas para obtener los retornos de los benchmarks en paralelo
        tasks = [self.get_returns(symbol, days) for symbol in benchmarks_to_fetch.keys()]
        benchmark_returns_list = await asyncio.gather(*tasks)
        
        # Mapear los resultados de vuelta a sus símbolos
        benchmark_returns_map = dict(zip(benchmarks_to_fetch.keys(), benchmark_returns_list))

        for symbol, benchmark_returns in benchmark_returns_map.items():
            if not benchmark_returns.empty:
                combined = pd.concat([main_returns, benchmark_returns], axis=1, join='inner')
                correlation = combined.iloc[:, 0].corr(combined.iloc[:, 1])
                correlation_results[benchmarks_to_fetch[symbol]] = round(correlation, 3) if not np.isnan(correlation) else 'N/A'
        
        return correlation_results