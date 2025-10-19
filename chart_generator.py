# chart_generator.py
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import pandas as pd

class ChartGenerator:
    """
    Genera gráficos interactivos de precios con proyecciones futuras.
    """
    def generate_prediction_chart(self, historical_data: pd.DataFrame, prediction_data: dict) -> str:
        """
        Crea un gráfico OHLC con una proyección de tendencia futura.

        Args:
            historical_data: DataFrame con datos OHLCV ('open', 'high', 'low', 'close').
            prediction_data: Diccionario con la predicción ('precio_predicho', 'horizonte_dias').

        Returns:
            Una cadena JSON que representa el objeto del gráfico de Plotly.
        """
        if historical_data.empty:
            return "{}"

        fig = go.Figure()

        # 1. Gráfico de velas (Candlestick) para datos históricos
        fig.add_trace(go.Candlestick(
            x=historical_data.index,
            open=historical_data['open'],
            high=historical_data['high'],
            low=historical_data['low'],
            close=historical_data['close'],
            name='Histórico',
            increasing_line_color='#03dac6', decreasing_line_color='#cf6679'
        ))

        # 2. Línea de proyección futura
        if prediction_data and 'precio_predicho' in prediction_data:
            last_close = historical_data['close'].iloc[-1]
            last_date = historical_data.index[-1]
            prediction_date = last_date + pd.Timedelta(days=prediction_data.get('horizonte_dias', 5))
            predicted_price = prediction_data['precio_predicho']

            fig.add_trace(go.Scatter(
                x=[last_date, prediction_date],
                y=[last_close, predicted_price],
                mode='lines+markers',
                name='Proyección ML',
                line=dict(color='#bb86fc', width=3, dash='dot'),
                marker=dict(size=10)
            ))

        # 3. Estilo del gráfico
        fig.update_layout(
            title=f"Proyección de Precio",
            yaxis_title="Precio (USDT)",
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30,30,30,0.8)'
        )

        return json.dumps(fig, cls=PlotlyJSONEncoder)