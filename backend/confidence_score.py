# ======================================================
# SIGNALCHECK – CONFIDENCE SCORE v2.1 (FIXED)
# ======================================================

def compute_confidence(module_results: dict):
    """
    Confianza del análisis basada en:
    - intensidad real de señales (solo positivas)
    - consistencia entre módulos activos
    """

    if not module_results:
        return 0.0

    # 🔥 SOLO señales positivas (riesgo real)
    positive_values = [v for v in module_results.values() if v > 0]

    if not positive_values:
        return 0.25  # ⚠️ contenido limpio → baja confianza estructural

    # --------------------------------------------------
    # INTENSIDAD PROMEDIO REAL
    # --------------------------------------------------
    avg_intensity = sum(positive_values) / len(positive_values)

    # --------------------------------------------------
    # CONSISTENCIA ENTRE MÓDULOS
    # --------------------------------------------------
    active_modules = len(positive_values)

    # Ajustado a tu engine (12+ módulos)
    consistency = min(active_modules / 5, 1.0)

    # --------------------------------------------------
    # BASE MÁS REALISTA
    # --------------------------------------------------
    confidence = 0.2

    confidence += avg_intensity * 0.5
    confidence += consistency * 0.3

    return round(min(confidence, 1.0), 2)