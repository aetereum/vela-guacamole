# quantum_trading.py
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.aqua.algorithms import VQE, QAOA
from qiskit.aqua.components.optimizers import COBYLA, SPSA
from qiskit.aqua.operators import WeightedPauliOperator
from qiskit.circuit.library import TwoLocal
import warnings
warnings.filterwarnings('ignore')

class QuantumPortfolioOptimizer:
    """Optimizador de portafolio usando computación cuántica"""
    
    def __init__(self):
        self.backend = Aer.get_backend('qasm_simulator')
        self.optimizer = COBYLA(maxiter=100)
        
    def optimizar_portafolio_cuantico(self, returns: np.ndarray, covariance: np.ndarray, 
                                    risk_aversion: float = 0.5):
        """Optimizar portafolio usando algoritmo cuántico"""
        n_assets = len(returns)
        
        # Formular el problema de optimización de portafolio
        pauli_list = self._portfolio_optimization_hamiltonian(returns, covariance, risk_aversion)
        qubit_op = WeightedPauliOperator(paulis=pauli_list)
        
        # Configurar ansatz (circuito cuántico)
        var_form = TwoLocal(n_assets, 'ry', 'cz', reps=3, entanglement='full')
        
        # Ejecutar VQE (Variational Quantum Eigensolver)
        vqe = VQE(qubit_op, var_form, self.optimizer)
        result = vqe.run(self.backend)
        
        # Obtener pesos óptimos
        optimal_weights = self._decode_solution(result['eigvecs'][0], n_assets)
        
        return {
            'optimal_weights': optimal_weights,
            'expected_return': np.dot(optimal_weights, returns),
            'portfolio_variance': optimal_weights @ covariance @ optimal_weights,
            'sharpe_ratio': np.dot(optimal_weights, returns) / np.sqrt(optimal_weights @ covariance @ optimal_weights),
            'quantum_circuit_depth': var_form.depth(),
            'execution_time': result['eval_time']
        }
    
    def _portfolio_optimization_hamiltonian(self, returns: np.ndarray, covariance: np.ndarray, 
                                          risk_aversion: float):
        """Crear Hamiltonian para optimización de portafolio"""
        n = len(returns)
        pauli_list = []
        
        # Término de retorno esperado (maximizar)
        for i in range(n):
            z_pauli = ['I'] * n
            z_pauli[i] = 'Z'
            pauli_str = ''.join(z_pauli)
            # Penalizar por no invertir (maximizar retorno)
            weight = -returns[i] * (1 - risk_aversion)
            pauli_list.append([weight, pauli_str])
        
        # Término de riesgo (minimizar varianza)
        for i in range(n):
            for j in range(n):
                if covariance[i, j] != 0:
                    z_pauli1 = ['I'] * n
                    z_pauli1[i] = 'Z'
                    z_pauli2 = ['I'] * n  
                    z_pauli2[j] = 'Z'
                    
                    pauli_str1 = ''.join(z_pauli1)
                    pauli_str2 = ''.join(z_pauli2)
                    
                    # Para términos diagonales
                    if i == j:
                        weight = risk_aversion * covariance[i, j]
                        pauli_list.append([weight, pauli_str1])
                    else:
                        # Para términos cruzados (simplificado)
                        weight = risk_aversion * covariance[i, j] / 2
                        pauli_list.append([weight, pauli_str1])
                        pauli_list.append([weight, pauli_str2])
        
        return pauli_list
    
    def _decode_solution(self, quantum_state, n_assets: int):
        """Decodificar estado cuántico a pesos de portafolio"""
        # Convertir estado cuántico a pesos normalizados
        weights = np.zeros(n_assets)
        
        for i in range(n_assets):
            # Mapear qubit i al peso del asset i
            # Esto es una simplificación - en implementación real usarías mediciones
            prob_0 = abs(quantum_state[i]) ** 2
            weights[i] = 1 - prob_0  # |1⟩ representa invertir
        
        # Normalizar pesos
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        
        return weights

class QuantumPatternRecognizer:
    """Reconocimiento de patrones de mercado usando quantum ML"""
    
    def __init__(self):
        self.backend = Aer.get_backend('qasm_simulator')
        
    def reconocer_patron_mercado(self, price_data: np.ndarray, pattern_type: str = 'trend'):
        """Reconocer patrones de mercado usando quantum circuits"""
        n_qubits = min(8, len(price_data))  # Máximo 8 qubits por limitaciones de simulación
        
        # Preparar datos cuánticos
        qc = self._encode_price_data(price_data[:n_qubits])
        
        # Aplicar circuito de reconocimiento de patrones
        if pattern_type == 'trend':
            qc = self._add_trend_recognition_circuit(qc, n_qubits)
        elif pattern_type == 'reversal':
            qc = self._add_reversal_recognition_circuit(qc, n_qubits)
        elif pattern_type == 'volatility':
            qc = self._add_volatility_circuit(qc, n_qubits)
        
        # Medir y obtener resultados
        cr = ClassicalRegister(n_qubits)
        qc.add_register(cr)
        qc.measure(range(n_qubits), range(n_qubits))
        
        # Ejecutar circuito
        job = execute(qc, self.backend, shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        # Analizar resultados
        pattern_confidence = self._analyze_quantum_results(counts, pattern_type)
        
        return {
            'pattern_type': pattern_type,
            'confidence': pattern_confidence,
            'quantum_circuit': qc,
            'measurement_counts': counts,
            'pattern_detected': pattern_confidence > 0.7
        }
    
    def _encode_price_data(self, price_data: np.ndarray) -> QuantumCircuit:
        """Codificar datos de precio en estado cuántico"""
        n_qubits = len(price_data)
        qr = QuantumRegister(n_qubits)
        qc = QuantumCircuit(qr)
        
        # Normalizar datos de precio
        normalized_data = (price_data - np.min(price_data)) / (np.max(price_data) - np.min(price_data))
        
        # Codificar usando rotaciones Y
        for i, value in enumerate(normalized_data):
            angle = np.arcsin(np.sqrt(value)) * 2  # Mapear a [0, π]
            qc.ry(angle, qr[i])
        
        return qc
    
    def _add_trend_recognition_circuit(self, qc: QuantumCircuit, n_qubits: int) -> QuantumCircuit:
        """Añadir circuito para reconocimiento de tendencias"""
        # Entrelazar qubits para detectar correlaciones (tendencias)
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        
        # Aplicar compuertas Hadamard para interferencia
        for i in range(n_qubits):
            qc.h(i)
        
        return qc
    
    def _add_reversal_recognition_circuit(self, qc: QuantumCircuit, n_qubits: int) -> QuantumCircuit:
        """Añadir circuito para reconocimiento de reversals"""
        # Patrón específico para detectar cambios de dirección
        for i in range(n_qubits - 2):
            # Toffoli gate para detectar patrones de tres puntos
            qc.ccx(i, i + 1, i + 2)
        
        # Fase gates para sensibilidad a cambios
        for i in range(n_qubits):
            qc.p(np.pi / 4, i)  # Phase shift
        
        return qc
    
    def _analyze_quantum_results(self, counts: dict, pattern_type: str) -> float:
        """Analizar resultados de medición cuántica"""
        total_shots = sum(counts.values())
        
        if pattern_type == 'trend':
            # Para tendencias, buscar estados con muchos 1s o muchos 0s
            trend_up = sum(count for bitstring, count in counts.items() if bitstring.count('1') > len(bitstring) * 0.7)
            trend_down = sum(count for bitstring, count in counts.items() if bitstring.count('0') > len(bitstring) * 0.7)
            confidence = max(trend_up, trend_down) / total_shots
        
        elif pattern_type == 'reversal':
            # Para reversals, buscar patrones alternantes
            reversal_patterns = 0
            for bitstring, count in counts.items():
                changes = sum(1 for i in range(1, len(bitstring)) if bitstring[i] != bitstring[i-1])
                if changes >= len(bitstring) * 0.6:  # Muchos cambios
                    reversal_patterns += count
            confidence = reversal_patterns / total_shots
        
        else:
            # Para volatilidad, buscar alta entropía
            max_entropy = len(next(iter(counts.keys()))) * np.log(2)
            entropy = -sum((count/total_shots) * np.log(count/total_shots) for count in counts.values())
            confidence = entropy / max_entropy
        
        return float(confidence)

class QuantumRiskManager:
    """Gestión de riesgo usando algoritmos cuánticos"""
    
    def __init__(self):
        self.portfolio_optimizer = QuantumPortfolioOptimizer()
        
    def calcular_var_cuantico(self, returns: np.ndarray, confidence_level: float = 0.95):
        """Calcular Value at Risk usando métodos cuánticos"""
        n_assets = len(returns)
        
        # Crear circuito cuántico para distribución de retornos
        qr = QuantumRegister(n_assets)
        cr = ClassicalRegister(n_assets)
        qc = QuantumCircuit(qr, cr)
        
        # Codificar distribución de retornos
        returns_normalized = (returns - np.min(returns)) / (np.max(returns) - np.min(returns))
        for i, ret in enumerate(returns_normalized):
            angle = np.arcsin(np.sqrt(ret)) * 2
            qc.ry(angle, qr[i])
        
        # Añadir gates para cálculo de percentiles
        qc.h(qr)  # Superposición para explorar distribución
        
        # Medir
        qc.measure(qr, cr)
        
        # Ejecutar
        backend = Aer.get_backend('qasm_simulator')
        job = execute(qc, backend, shots=8192)
        result = job.result()
        counts = result.get_counts()
        
        # Calcular VaR desde distribución cuántica
        var_result = self._calculate_var_from_quantum(counts, returns, confidence_level)
        
        return {
            'var': var_result,
            'confidence_level': confidence_level,
            'quantum_distribution': counts,
            'circuit_depth': qc.depth()
        }
    
    def _calculate_var_from_quantum(self, counts: dict, returns: np.ndarray, confidence_level: float) -> float:
        """Calcular VaR desde distribución cuántica"""
        total_shots = sum(counts.values())
        
        # Convertir counts a distribución de retornos
        return_values = []
        probabilities = []
        
        for bitstring, count in counts.items():
            # Mapear bitstring a retorno (simplificado)
            binary_val = int(bitstring, 2)
            max_val = 2 ** len(bitstring) - 1
            normalized_ret = binary_val / max_val
            mapped_ret = np.min(returns) + normalized_ret * (np.max(returns) - np.min(returns))
            
            return_values.append(mapped_ret)
            probabilities.append(count / total_shots)
        
        # Ordenar por retorno
        sorted_returns = sorted(return_values)
        sorted_probs = [p for _, p in sorted(zip(return_values, probabilities))]
        
        # Calcular VaR
        cumulative_prob = 0
        for ret, prob in zip(sorted_returns, sorted_probs):
            cumulative_prob += prob
            if cumulative_prob >= (1 - confidence_level):
                return ret
        
        return sorted_returns[0]  # Fallback