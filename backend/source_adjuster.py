# ======================================================
# SIGNALCHECK – SOURCE ADJUSTER v2.0 (SMOOTH)
# ======================================================

def adjust_score_by_source(risk_score: float, source_info: dict):
    """
    Ajuste progresivo según confianza de fuente
    """

    trust = source_info.get("trust_level", 0.5)

    # --------------------------------------------------
    # FACTOR DINÁMICO
    # --------------------------------------------------
    # trust = 0.0 → factor = 1.25 (más riesgo)
    # trust = 0.5 → factor = 1.0 (neutral)
    # trust = 1.0 → factor = 0.75 (menos riesgo)
    # --------------------------------------------------

    factor = 1.25 - (trust * 0.5)

    risk_score *= factor

    # --------------------------------------------------
    # CLAMP FINAL
    # --------------------------------------------------
    return max(min(risk_score, 1.0), 0.0)