def detectar_instituciones(datos):
    """Detecta patrones de trading institucional"""
    # Grandes volúmenes en apertura/cierre
    volumen_alto = datos['Volume'] > datos['Volume'].rolling(20).mean() * 2
    movimiento_significativo = datos['Close'].pct_change().abs() > 0.015
    
    return volumen_alto & movimiento_significativo