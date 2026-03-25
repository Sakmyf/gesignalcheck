# ======================================================
# SIGNALCHECK – CONFIDENCE SCORE v2.0 (REAL)
# ======================================================

def compute_confidence(module_results: dict):
    """
    Confianza del análisis basada en:
    - intensidad de señales
    - consistencia entre módulos
    """

    if not module_results:
        return 0.0

    values = list(module_results.values())

    active_modules = sum(1 for v in values if v > 0.05)
    avg_intensity  = sum(values) / max(len(values), 1)

    consistency = min(active_modules / 6, 1.0)

    confidence = 0.4
    confidence += avg_intensity * 0.3
    confidence += consistency * 0.3

    return round(min(confidence, 1.0), 2)