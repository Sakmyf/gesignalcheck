# ======================================================
# SIGNALCHECK – SOURCE ADJUSTER v2.1 (STRONG SMOOTH)
# ======================================================

def adjust_score_by_source(risk_score: float, source_info: dict):
    """
    Ajuste progresivo pero con impacto real
    """

    trust = source_info.get("trust_level", 0.5)

    # --------------------------------------------------
    # NUEVO FACTOR MÁS POTENTE
    # --------------------------------------------------
    # trust = 1.0 → factor = 0.35 (fuerte reducción)
    # trust = 0.8 → factor = 0.5
    # trust = 0.5 → factor = 1.0
    # trust = 0.3 → factor = 1.15
    # --------------------------------------------------

    factor = 1.3 - (trust * 1.0)

    risk_score *= factor

    # --------------------------------------------------
    # EXTRA BOOST PARA FUENTES MUY CONFIABLES
    # --------------------------------------------------
    if trust >= 0.85:
        risk_score *= 0.7

    # --------------------------------------------------
    # CLAMP FINAL
    # --------------------------------------------------
    return max(min(risk_score, 1.0), 0.0)