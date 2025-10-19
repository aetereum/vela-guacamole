# blockchain_defi_integration.py
import asyncio
import aiohttp
import json
import hmac
import hashlib
from web3 import Web3
from decimal import Decimal
from typing import Dict, List, Optional
import ccxt
from datetime import datetime
import pandas as pd

class BlockchainAnalyzer:
    """Analizador de datos blockchain y DeFi"""
    
    def __init__(self, config):
        self.config = config
        self.web3_providers = {
            'ethereum': Web3(Web3.HTTPProvider(config['ethereum_rpc'])),
            'polygon': Web3(Web3.HTTPProvider(config['polygon_rpc'])),
            'arbitrum': Web3(Web3.HTTPProvider(config['arbitrum_rpc']))
        }
        self.cex_exchanges = {}
        self.dex_exchanges = {}
        
        # Inicializar exchanges
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Inicializar conexiones con exchanges"""
        # CEX (Centralized Exchanges)
        self.cex_exchanges['binance'] = ccxt.binance({
            'apiKey': self.config.get('binance_api_key', ''),
            'secret': self.config.get('binance_secret_key', ''),
            'enableRateLimit': True
        })
        
        # DEX (Decentralized Exchanges) - usando APIs
        self.dex_exchanges['uniswap'] = UniswapAPI(self.config)
        self.dex_exchanges['pancakeswap'] = PancakeSwapAPI(self.config)
    
    async def analizar_whale_activity(self, token_address: str, chain: str = 'ethereum'):
        """Analizar actividad de ballenas en blockchain"""
        try:
            web3 = self.web3_providers.get(chain)
            if not web3:
                return {'error': f'Chain {chain} no configurada'}
            
            # Obtener transacciones recientes del token
            transactions = await self._get_token_transactions(token_address, chain)
            
            # Identificar transacciones grandes (whales)
            whale_threshold = Decimal('100000')  # $100k en USD
            whale_transactions = []
            
            for tx in transactions:
                value_usd = await self._get_token_value_usd(tx['value'], token_address, chain)
                if value_usd >= whale_threshold:
                    whale_transactions.append({
                        'hash': tx['hash'],
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': tx['value'],
                        'value_usd': value_usd,
                        'timestamp': tx['timestamp'],
                        'type': 'COMPRA' if tx['to'] == 'exchange_address' else 'VENTA'
                    })
            
            # Analizar patrones de whales
            whale_analysis = self._analyze_whale_patterns(whale_transactions)
            
            return {
                'token_address': token_address,
                'chain': chain,
                'whale_transactions_count': len(whale_transactions),
                'total_whale_volume_usd': sum(tx['value_usd'] for tx in whale_transactions),
                'whale_activity_score': whale_analysis['activity_score'],
                'sentiment': whale_analysis['sentiment'],
                'transactions': whale_transactions[:10]  # Top 10
            }
            
        except Exception as e:
            return {'error': f'Error analizando whale activity: {e}'}
    
    async def _get_token_transactions(self, token_address: str, chain: str):
        """Obtener transacciones recientes de un token"""
        # Implementación simplificada - en producción usarías APIs como Etherscan
        # o servicios como The Graph para consultas eficientes
        return []  # Placeholder
    
    async def analizar_liquidity_pools(self, token_address: str, dex: str = 'uniswap'):
        """Analizar pools de liquidez en DEX"""
        try:
            dex_api = self.dex_exchanges.get(dex)
            if not dex_api:
                return {'error': f'DEX {dex} no configurado'}
            
            # Obtener datos del pool
            pool_data = await dex_api.get_pool_data(token_address)
            
            # Analizar métricas de liquidez
            liquidity_analysis = {
                'total_liquidity_usd': pool_data['total_liquidity'],
                'liquidity_change_24h': pool_data['liquidity_change_24h'],
                'volume_24h': pool_data['volume_24h'],
                'fees_24h': pool_data['fees_24h'],
                'concentration': self._calculate_liquidity_concentration(pool_data),
                'impermanent_loss_risk': self._calculate_impermanent_loss_risk(pool_data)
            }
            
            return {
                'token_address': token_address,
                'dex': dex,
                'liquidity_metrics': liquidity_analysis,
                'pool_health_score': self._calculate_pool_health_score(liquidity_analysis),
                'recommendation': self._generate_liquidity_recommendation(liquidity_analysis)
            }
            
        except Exception as e:
            return {'error': f'Error analizando liquidity pools: {e}'}
    
    def _calculate_liquidity_concentration(self, pool_data: Dict) -> float:
        """Calcular concentración de liquidez"""
        # Implementar cálculo basado en distribución de liquidez
        return 0.0  # Placeholder
    
    def _calculate_impermanent_loss_risk(self, pool_data: Dict) -> str:
        """Calcular riesgo de impermanent loss"""
        volatility = pool_data.get('volatility', 0)
        if volatility > 0.8:
            return 'ALTO'
        elif volatility > 0.5:
            return 'MEDIO'
        else:
            return 'BAJO'
    
    def _calculate_pool_health_score(self, metrics: Dict) -> float:
        """Calcular score de salud del pool"""
        score = 0.0
        score += min(metrics['total_liquidity_usd'] / 1000000, 1.0) * 0.3
        score += max(metrics['liquidity_change_24h'] + 1, 0) * 0.2
        score += min(metrics['volume_24h'] / metrics['total_liquidity_usd'], 2.0) * 0.3
        score += (1 - metrics['impermanent_loss_risk']) * 0.2
        return min(score, 1.0)
    
    async def analizar_yield_farming(self, protocol: str):
        """Analizar oportunidades de yield farming"""
        try:
            protocols_data = {
                'aave': await self._analyze_aave_yield(),
                'compound': await self._analyze_compound_yield(),
                'curve': await self._analyze_curve_yield(),
                'yearn': await self._analyze_yearn_yield()
            }
            
            protocol_data = protocols_data.get(protocol.lower())
            if not protocol_data:
                return {'error': f'Protocolo {protocol} no soportado'}
            
            # Calcular APY ajustado por riesgo
            risk_adjusted_apy = self._calculate_risk_adjusted_apy(protocol_data)
            
            return {
                'protocol': protocol,
                'apy_base': protocol_data['apy'],
                'apy_risk_adjusted': risk_adjusted_apy,
                'tvl': protocol_data['tvl'],
                'risk_score': protocol_data['risk_score'],
                'opportunity_score': risk_adjusted_apy * protocol_data['tvl'] / 1000000,
                'recommended_assets': protocol_data['top_assets'][:3]
            }
            
        except Exception as e:
            return {'error': f'Error analizando yield farming: {e}'}
    
    def _calculate_risk_adjusted_apy(self, protocol_data: Dict) -> float:
        """Calcular APY ajustado por riesgo"""
        base_apy = protocol_data['apy']
        risk_score = protocol_data['risk_score']  # 0-1, donde 1 es más riesgoso
        risk_adjustment = 1 - (risk_score * 0.5)  # Reducir APY hasta 50% por riesgo
        return base_apy * risk_adjustment

class DeFiArbitrageFinder:
    """Encontrador de oportunidades de arbitraje DeFi"""
    
    def __init__(self, config):
        self.config = config
        self.exchanges = {}
        self._initialize_exchanges()
    
    def _initialize_exchanges(self):
        """Inicializar conexiones con múltiples exchanges"""
        exchanges_config = {
            'binance': {'apiKey': self.config.get('binance_api_key'), 'secret': self.config.get('binance_secret')},
            'kraken': {'apiKey': self.config.get('kraken_api_key'), 'secret': self.config.get('kraken_secret')},
            'uniswap': {'rpc_url': self.config.get('ethereum_rpc')},
            'sushiswap': {'rpc_url': self.config.get('ethereum_rpc')}
        }
        
        for name, config in exchanges_config.items():
            if all(config.values()):  # Solo inicializar si hay credenciales
                try:
                    if name in ['binance', 'kraken']:
                        self.exchanges[name] = getattr(ccxt, name)(config)
                    else:
                        self.exchanges[name] = DexExchange(name, config)
                except Exception as e:
                    print(f"❌ Error inicializando {name}: {e}")
    
    async def find_arbitrage_opportunities(self, symbols: List[str]):
        """Encontrar oportunidades de arbitraje entre exchanges"""
        opportunities = []
        
        for symbol in symbols:
            try:
                prices = await self._get_prices_across_exchanges(symbol)
                arbitrage_data = self._calculate_arbitrage_opportunities(symbol, prices)
                
                if arbitrage_data['max_spread'] > 0.02:  # 2% spread mínimo
                    opportunities.append(arbitrage_data)
                    
            except Exception as e:
                print(f"❌ Error analizando {symbol}: {e}")
                continue
        
        # Ordenar por mejor oportunidad
        opportunities.sort(key=lambda x: x['max_spread'], reverse=True)
        
        return {
            'total_opportunities': len(opportunities),
            'best_opportunity': opportunities[0] if opportunities else None,
            'opportunities': opportunities[:5]  # Top 5
        }
    
    async def _get_prices_across_exchanges(self, symbol: str) -> Dict[str, float]:
        """Obtener precios a través de múltiples exchanges"""
        prices = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                if hasattr(exchange, 'fetch_ticker'):
                    # CEX
                    ticker = exchange.fetch_ticker(symbol)
                    prices[exchange_name] = ticker['last']
                else:
                    # DEX
                    price = await exchange.get_price(symbol)
                    prices[exchange_name] = price
                    
                # Pequeña pausa para no sobrecargar APIs
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error obteniendo precio de {exchange_name} para {symbol}: {e}")
                continue
        
        return prices
    
    def _calculate_arbitrage_opportunities(self, symbol: str, prices: Dict[str, float]) -> Dict:
        """Calcular oportunidades de arbitraje"""
        if len(prices) < 2:
            return {'error': 'No hay suficientes precios para comparar'}
        
        exchanges = list(prices.keys())
        max_spread = 0
        best_pair = None
        
        # Encontrar el mayor spread entre exchanges
        for i, ex1 in enumerate(exchanges):
            for ex2 in exchanges[i+1:]:
                price1 = prices[ex1]
                price2 = prices[ex2]
                
                if price1 and price2 and price1 > 0 and price2 > 0:
                    spread = abs(price1 - price2) / min(price1, price2)
                    
                    if spread > max_spread:
                        max_spread = spread
                        best_pair = {
                            'buy_exchange': ex1 if price1 < price2 else ex2,
                            'sell_exchange': ex2 if price1 < price2 else ex1,
                            'buy_price': min(price1, price2),
                            'sell_price': max(price1, price2),
                            'spread': spread
                        }
        
        return {
            'symbol': symbol,
            'max_spread': max_spread,
            'best_opportunity': best_pair,
            'all_prices': prices,
            'timestamp': datetime.now()
        }
    
    async def execute_arbitrage(self, opportunity: Dict, amount: float):
        """Ejecutar operación de arbitraje"""
        try:
            buy_exchange = self.exchanges[opportunity['buy_exchange']]
            sell_exchange = self.exchanges[opportunity['sell_exchange']]
            
            # Comprar en exchange con precio bajo
            buy_order = await buy_exchange.create_order(
                opportunity['symbol'], 
                'market', 
                'buy', 
                amount, 
                opportunity['buy_price']
            )
            
            # Vender en exchange con precio alto
            sell_order = await sell_exchange.create_order(
                opportunity['symbol'],
                'market',
                'sell',
                amount,
                opportunity['sell_price']
            )
            
            # Calcular profit
            profit = (sell_order['cost'] - buy_order['cost']) - self._calculate_fees(buy_order, sell_order)
            
            return {
                'success': True,
                'profit': profit,
                'profit_percentage': profit / buy_order['cost'],
                'buy_order': buy_order,
                'sell_order': sell_order
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'profit': 0
            }
    
    def _calculate_fees(self, buy_order: Dict, sell_order: Dict) -> float:
        """Calcular fees totales de la operación"""
        buy_fees = buy_order.get('fee', {}).get('cost', 0) or 0
        sell_fees = sell_order.get('fee', {}).get('cost', 0) or 0
        return buy_fees + sell_fees

class UniswapAPI:
    """Cliente para API de Uniswap"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    
    async def get_pool_data(self, token_address: str):
        """Obtener datos del pool de Uniswap"""
        # Implementación usando The Graph API
        query = """
        query {
            pools(where: {token0: "%s"}) {
                id
                totalValueLockedUSD
                volumeUSD
                feesUSD
                token0Price
                token1Price
            }
        }
        """ % token_address
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json={'query': query}) as response:
                data = await response.json()
                return self._parse_pool_data(data)
    
    def _parse_pool_data(self, data: Dict) -> Dict:
        """Parsear datos del pool"""
        pools = data.get('data', {}).get('pools', [])
        if not pools:
            return {}
        
        pool = pools[0]
        return {
            'total_liquidity': float(pool['totalValueLockedUSD']),
            'volume_24h': float(pool['volumeUSD']),
            'fees_24h': float(pool['feesUSD']),
            'price_token0': float(pool['token0Price']),
            'price_token1': float(pool['token1Price'])
        }

class PancakeSwapAPI:
    """Cliente para API de PancakeSwap"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://api.pancakeswap.info/api/v2"
    
    async def get_pool_data(self, token_address: str):
        """Obtener datos del pool de PancakeSwap"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tokens/{token_address}") as response:
                data = await response.json()
                return self._parse_token_data(data)
    
    def _parse_token_data(self, data: Dict) -> Dict:
        """Parsear datos del token"""
        token_data = data.get('data', {})
        return {
            'total_liquidity': float(token_data.get('liquidity', 0)),
            'price': float(token_data.get('price', 0)),
            'price_BNB': float(token_data.get('price_BNB', 0))
        }