# datos_alternativos_analyzer.py
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import aiohttp
from textblob import TextBlob
import re
from collections import Counter

class DatosAlternativosAnalyzer:
    """Analizador de datos alternativos para alpha generation"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.web_traffic_data = {}
        
    async def analizar_sentimiento_redes_avanzado(self, simbolo: str):
        """Análisis avanzado de sentimiento en redes sociales"""
        sources = {
            'twitter': await self._analizar_twitter(simbolo),
            'reddit': await self._analizar_reddit(simbolo),
            'news': await self._analizar_noticias(simbolo),
            'youtube': await self._analizar_youtube(simbolo)
        }
        
        # Combinar análisis de todas las fuentes
        combined_sentiment = self._combinar_sentimientos(sources)
        
        return {
            'simbolo': simbolo,
            'sentimiento_combinado': combined_sentiment,
            'fuentes': sources,
            'timestamp': datetime.now()
        }
    
    async def _analizar_twitter(self, simbolo: str):
        """Análisis de Twitter con API v2"""
        try:
            # Buscar tweets recientes (implementación simplificada)
            query = f"${simbolo} OR #{simbolo} -is:retweet"
            
            # Análisis de volumen y sentimiento
            sentiment_scores = []
            mention_count = 0
            influencer_mentions = 0
            
            # Palabras clave positivas/negativas específicas de trading
            positive_keywords = ['bull', 'bullish', 'buy', 'long', 'moon', 'rocket', 'growth', 'earnings beat']
            negative_keywords = ['bear', 'bearish', 'sell', 'short', 'crash', 'drop', 'miss', 'warning']
            
            # Simulación de análisis (en producción usarías API de Twitter)
            simulated_tweets = [
                f"${simbolo} looking bullish today! Great earnings report.",
                f"Thinking of going long on ${simbolo}, technicals look good.",
                f"${simbolo}担心市场调整",  # Chino: preocupado por ajuste
                f"Short ${simbolo} before earnings, too much hype."
            ]
            
            for tweet in simulated_tweets:
                sentiment = self._analizar_sentimiento_texto_avanzado(tweet)
                sentiment_scores.append(sentiment)
                mention_count += 1
                
                # Detectar influencers (seguidores > 10k en producción)
                if any(word in tweet.lower() for word in ['analyst', 'expert', 'recommends']):
                    influencer_mentions += 1
            
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.5
            sentiment_trend = 'POSITIVO' if avg_sentiment > 0.6 else 'NEGATIVO' if avg_sentiment < 0.4 else 'NEUTRAL'
            
            return {
                'mention_count': mention_count,
                'influencer_mentions': influencer_mentions,
                'avg_sentiment': avg_sentiment,
                'sentiment_trend': sentiment_trend,
                'sentiment_scores': sentiment_scores
            }
            
        except Exception as e:
            return {'error': f'Twitter analysis error: {e}'}
    
    async def _analizar_reddit(self, simbolo: str):
        """Análisis de Reddit (WallStreetBets, investing, etc.)"""
        try:
            subreddits = ['wallstreetbets', 'investing', 'stocks']
            combined_analysis = {}
            
            for subreddit in subreddits:
                # Simulación de datos de Reddit
                posts = [
                    f"DD: ${simbolo} is undervalued by 50%",
                    f"${simbolo} to the moon! 🚀",
                    f"Why I'm shorting ${simbolo}",
                    f"${simbolo} earnings discussion"
                ]
                
                post_sentiments = [self._analizar_sentimiento_texto_avanzado(post) for post in posts]
                avg_sentiment = np.mean(post_sentiments) if post_sentiments else 0.5
                
                combined_analysis[subreddit] = {
                    'post_count': len(posts),
                    'avg_sentiment': avg_sentiment,
                    'hype_score': min(len(posts) * avg_sentiment, 10)  # Score de 0-10
                }
            
            overall_sentiment = np.mean([data['avg_sentiment'] for data in combined_analysis.values()])
            
            return {
                'subreddits_analyzed': combined_analysis,
                'overall_sentiment': overall_sentiment,
                'total_hype_score': sum(data['hype_score'] for data in combined_analysis.values())
            }
            
        except Exception as e:
            return {'error': f'Reddit analysis error: {e}'}
    
    async def analizar_datos_web_traffic(self, simbolo: str):
        """Analizar tráfico web y búsquedas (SimilarWeb, Google Trends)"""
        try:
            # Simulación de datos de tráfico web
            traffic_data = {
                'website_visits': np.random.randint(100000, 500000),
                'visit_growth': np.random.uniform(-0.1, 0.3),
                'time_on_site': np.random.uniform(2, 10),
                'bounce_rate': np.random.uniform(0.3, 0.7)
            }
            
            # Análisis de Google Trends (simulado)
            trends_data = {
                'search_volume': np.random.randint(50, 100),
                'trend_direction': np.random.choice(['UP', 'DOWN', 'STABLE']),
                'related_queries': [f'{simbolo} stock', f'{simbolo} earnings', f'buy {simbolo}']
            }
            
            # Calcular score de engagement
            engagement_score = (
                traffic_data['website_visits'] / 100000 * 0.3 +
                max(traffic_data['visit_growth'], 0) * 0.3 +
                (10 - traffic_data['time_on_site']) * 0.2 +
                (1 - traffic_data['bounce_rate']) * 0.2
            )
            
            return {
                'traffic_metrics': traffic_data,
                'search_trends': trends_data,
                'engagement_score': engagement_score,
                'interpretation': self._interpretar_engagement(engagement_score)
            }
            
        except Exception as e:
            return {'error': f'Web traffic analysis error: {e}'}
    
    def _analizar_sentimiento_texto_avanzado(self, texto: str) -> float:
        """Análisis de sentimiento avanzado con contexto financiero"""
        # Diccionario financiero personalizado
        financial_lexicon = {
            'positive': {
                'bullish': 0.8, 'moon': 0.9, 'rocket': 0.9, 'growth': 0.7,
                'earnings beat': 0.8, 'upgrade': 0.7, 'buy': 0.6, 'long': 0.6,
                'undervalued': 0.7, 'breakout': 0.6, 'rally': 0.7
            },
            'negative': {
                'bearish': -0.8, 'crash': -0.9, 'drop': -0.7, 'miss': -0.8,
                'downgrade': -0.7, 'sell': -0.6, 'short': -0.6, 'overvalued': -0.7,
                'breakdown': -0.6, 'collapse': -0.9, 'warning': -0.7
            }
        }
        
        texto_lower = texto.lower()
        
        # Análisis con TextBlob
        try:
            blob = TextBlob(texto)
            base_sentiment = (blob.sentiment.polarity + 1) / 2  # Convertir a 0-1
        except:
            base_sentiment = 0.5
        
        # Ajustar con léxico financiero
        financial_score = 0
        financial_words = 0
        
        for word, score in financial_lexicon['positive'].items():
            if word in texto_lower:
                financial_score += score
                financial_words += 1
        
        for word, score in financial_lexicon['negative'].items():
            if word in texto_lower:
                financial_score += score
                financial_words += 1
        
        if financial_words > 0:
            financial_sentiment = (financial_score / financial_words + 1) / 2  # Convertir a 0-1
            # Combinar sentimientos (70% peso al financiero)
            combined_sentiment = financial_sentiment * 0.7 + base_sentiment * 0.3
        else:
            combined_sentiment = base_sentiment
        
        return combined_sentiment
    
    def _combinar_sentimientos(self, sources: dict) -> dict:
        """Combinar sentimientos de múltiples fuentes"""
        valid_sources = {k: v for k, v in sources.items() if 'error' not in v}
        
        if not valid_sources:
            return {'error': 'No valid sentiment data'}
        
        sentiments = []
        weights = {
            'twitter': 0.4,
            'reddit': 0.3,
            'news': 0.2,
            'youtube': 0.1
        }
        
        for source, data in valid_sources.items():
            if 'avg_sentiment' in data:
                sentiments.append(data['avg_sentiment'] * weights.get(source, 0.1))
            elif 'overall_sentiment' in data:
                sentiments.append(data['overall_sentiment'] * weights.get(source, 0.1))
        
        if not sentiments:
            return {'error': 'No sentiment scores available'}
        
        combined_score = sum(sentiments) / sum(weights.get(s, 0.1) for s in valid_sources.keys())
        
        return {
            'score': combined_score,
            'trend': 'POSITIVO' if combined_score > 0.6 else 'NEGATIVO' if combined_score < 0.4 else 'NEUTRAL',
            'confidence': min(len(valid_sources) * 0.2, 0.9),
            'sources_used': list(valid_sources.keys())
        }
    
    def _interpretar_engagement(self, score: float) -> str:
        """Interpretar score de engagement"""
        if score > 0.7:
            return 'ALTO_ENGAGEMENT'
        elif score > 0.4:
            return 'MEDIO_ENGAGEMENT'
        else:
            return 'BAJO_ENGAGEMENT'
    
    async def _analizar_noticias(self, simbolo: str):
        """Análisis de sentimiento en noticias"""
        # Implementación simplificada
        return {
            'article_count': np.random.randint(5, 20),
            'avg_sentiment': np.random.uniform(0.3, 0.8),
            'major_news': ['Earnings Report', 'Analyst Upgrade', 'Product Launch']
        }
    
    async def _analizar_youtube(self, simbolo: str):
        """Análisis de sentimiento en YouTube"""
        # Implementación simplificada
        return {
            'video_count': np.random.randint(3, 15),
            'avg_sentiment': np.random.uniform(0.4, 0.9),
            'total_views': np.random.randint(10000, 500000)
        }