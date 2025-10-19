# reinforcement_learning_trader.py
import numpy as np
import pandas as pd
import gym
from gym import spaces
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import check_env
import torch
from torch import nn
import warnings
warnings.filterwarnings('ignore')

class TradingEnvironment(gym.Env):
    """Entorno personalizado de trading para Reinforcement Learning"""
    
    def __init__(self, df, initial_balance=10000, lookback_window=50):
        super(TradingEnvironment, self).__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.lookback_window = lookback_window
        self.current_step = lookback_window
        
        # Definir espacios de acción y observación
        # Acciones: 0=Mantener, 1=Comprar, 2=Vender, 3=Cerrar posición
        self.action_space = spaces.Discrete(4)
        
        # Espacio de observación: precios, indicadores, portfolio
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(lookback_window * 8 + 3,),  # 8 características por paso + 3 del portfolio
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self):
        """Resetear el entorno"""
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.current_step = self.lookback_window
        
        return self._next_observation()
    
    def _next_observation(self):
        """Obtener la siguiente observación"""
        frame = np.array([
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'Open'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'High'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'Low'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'Close'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'Volume'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'RSI'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'MACD'].values,
            self.df.loc[self.current_step - self.lookback_window:self.current_step, 'BB_width'].values,
        ])
        
        # Aplanar y agregar información del portfolio
        obs = frame.flatten()
        obs = np.append(obs, [
            self.balance,
            self.shares_held,
            self.cost_basis
        ])
        
        return obs.astype(np.float32)
    
    def _take_action(self, action):
        """Ejecutar acción en el entorno"""
        current_price = self.df.loc[self.current_step, 'Close']
        action_type = action
        
        if action_type == 0:  # Mantener
            pass
            
        elif action_type == 1 and self.balance > 0:  # Comprar
            # Comprar con el 10% del balance
            shares_to_buy = int((self.balance * 0.1) / current_price)
            if shares_to_buy > 0:
                additional_cost = shares_to_buy * current_price
                self.balance -= additional_cost
                self.shares_held += shares_to_buy
                self.cost_basis = (self.cost_basis * (self.shares_held - shares_to_buy) + additional_cost) / self.shares_held
                
        elif action_type == 2 and self.shares_held > 0:  # Vender
            # Vender el 10% de las acciones
            shares_to_sell = int(self.shares_held * 0.1)
            if shares_to_sell > 0:
                self.balance += shares_to_sell * current_price
                self.shares_held -= shares_to_sell
                self.total_shares_sold += shares_to_sell
                self.total_sales_value += shares_to_sell * current_price
                
        elif action_type == 3 and self.shares_held > 0:  # Cerrar posición
            self.balance += self.shares_held * current_price
            self.shares_held = 0
            self.cost_basis = 0
        
        # Calcular net worth
        self.net_worth = self.balance + self.shares_held * current_price
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
    
    def step(self, action):
        """Dar un paso en el entorno"""
        self._take_action(action)
        self.current_step += 1
        
        # Calcular reward
        reward = self._calculate_reward()
        
        # Verificar si el episodio terminó
        done = self.net_worth <= 0 or self.current_step >= len(self.df) - 1
        
        # Observación del siguiente paso
        obs = self._next_observation()
        
        return obs, reward, done, {}
    
    def _calculate_reward(self):
        """Calcular reward basado en performance"""
        current_price = self.df.loc[self.current_step, 'Close']
        net_worth = self.balance + self.shares_held * current_price
        
        # Reward base por cambio en net worth
        reward = (net_worth - self.initial_balance) / self.initial_balance
        
        # Penalizar por drawdown excesivo
        drawdown = (self.max_net_worth - net_worth) / self.max_net_worth
        if drawdown > 0.1:  # 10% drawdown
            reward -= drawdown * 10
        
        # Recompensar por trades exitosos
        if self.total_shares_sold > 0:
            avg_sell_price = self.total_sales_value / self.total_shares_sold
            if avg_sell_price > self.cost_basis:
                reward += 0.1
        
        return reward
    
    def render(self, mode='human'):
        """Renderizar el estado actual"""
        profit = self.net_worth - self.initial_balance
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance:.2f}')
        print(f'Shares held: {self.shares_held}')
        print(f'Net worth: {self.net_worth:.2f}')
        print(f'Profit: {profit:.2f}')

class RLTrader:
    """Sistema de Trading con Reinforcement Learning"""
    
    def __init__(self):
        self.models = {}
        self.training_data = {}
        
    def preparar_datos_rl(self, df):
        """Preparar datos para RL"""
        # Calcular indicadores técnicos
        df['RSI'] = self._calcular_rsi(df['Close'])
        df['MACD'] = self._calcular_macd(df['Close'])
        df['BB_width'] = self._calcular_bb_width(df['Close'])
        
        return df.dropna()
    
    def _calcular_rsi(self, prices, window=14):
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calcular_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcular MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calcular_bb_width(self, prices, window=20):
        """Calcular Bollinger Bands Width"""
        sma = prices.rolling(window).mean()
        std = prices.rolling(window).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return (upper_band - lower_band) / sma
    
    def entrenar_modelo_rl(self, simbolo, df, algoritmo='PPO', timesteps=50000):
        """Entrenar modelo de RL"""
        print(f"🤖 Entrenando modelo {algoritmo} para {simbolo}...")
        
        # Preparar datos
        df_preparado = self.preparar_datos_rl(df)
        
        # Crear entorno
        env = DummyVecEnv([lambda: TradingEnvironment(df_preparado)])
        
        # Seleccionar algoritmo
        if algoritmo == 'PPO':
            model = PPO('MlpPolicy', env, verbose=1, 
                       learning_rate=0.0003,
                       n_steps=2048,
                       batch_size=64,
                       n_epochs=10,
                       gamma=0.99,
                       gae_lambda=0.95,
                       clip_range=0.2,
                       ent_coef=0.01)
        elif algoritmo == 'A2C':
            model = A2C('MlpPolicy', env, verbose=1,
                       learning_rate=0.0007,
                       n_steps=5,
                       gamma=0.99,
                       gae_lambda=1.0,
                       ent_coef=0.01)
        elif algoritmo == 'DQN':
            model = DQN('MlpPolicy', env, verbose=1,
                       learning_rate=0.0001,
                       buffer_size=10000,
                       learning_starts=1000,
                       batch_size=32,
                       tau=1.0,
                       gamma=0.99,
                       train_freq=4,
                       gradient_steps=1,
                       target_update_interval=1000,
                       exploration_fraction=0.1,
                       exploration_initial_eps=1.0,
                       exploration_final_eps=0.05)
        
        # Entrenar modelo
        model.learn(total_timesteps=timesteps)
        
        # Guardar modelo
        self.models[simbolo] = model
        self.training_data[simbolo] = df_preparado
        
        print(f"✅ Modelo {algoritmo} entrenado para {simbolo}")
        return model
    
    def predecir_accion_rl(self, simbolo, datos_actuales):
        """Predecir acción usando RL"""
        if simbolo not in self.models:
            return {'error': f'Modelo no entrenado para {simbolo}'}
        
        model = self.models[simbolo]
        
        # Preparar datos actuales
        datos_preparados = self.preparar_datos_rl(datos_actuales)
        
        # Crear entorno para predicción
        env = TradingEnvironment(datos_preparados)
        obs = env.reset()
        
        # Predecir acción
        action, _states = model.predict(obs, deterministic=True)
        
        # Mapear acción a significado
        action_map = {
            0: 'MANTENER',
            1: 'COMPRAR', 
            2: 'VENDER',
            3: 'CERRAR_POSICION'
        }
        
        return {
            'accion': action_map[action],
            'confianza': 0.7,  # Placeholder - en realidad necesitaríamos probabilidades
            'modelo': 'RL_' + type(model).__name__,
            'timestamp': pd.Timestamp.now()
        }
    
    def evaluar_modelo_rl(self, simbolo, datos_test):
        """Evaluar modelo de RL en datos de test"""
        if simbolo not in self.models:
            return {'error': f'Modelo no entrenado para {simbolo}'}
        
        model = self.models[simbolo]
        datos_preparados = self.preparar_datos_rl(datos_test)
        
        env = TradingEnvironment(datos_preparados)
        obs = env.reset()
        
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
        
        return {
            'total_reward': total_reward,
            'steps': steps,
            'final_balance': env.balance,
            'final_net_worth': env.net_worth,
            'profit': env.net_worth - env.initial_balance,
            'return_percentage': (env.net_worth - env.initial_balance) / env.initial_balance * 100
        }