# ======================================================
# SIGNALCHECK – CONFIDENCE SCORE v1.0
# Qué tan confiable es el análisis
# ======================================================

def compute_confidence(signals: list, patterns: list):
    """
    Calcula la confianza del análisis
    """

    base = 0.5

    # Más señales → más confianza
    base += min(len(signals) * 0.05, 0.3)

    # Más patrones → más robusto
    base += min(len(patterns) * 0.1, 0.2)

    return max(min(base, 1.0), 0.0)