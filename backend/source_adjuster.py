# ======================================================
# SIGNALCHECK – SOURCE ADJUSTER v1.0
# Ajusta el score según la fuente
# ======================================================

def adjust_score_by_source(risk_score: float, source_info: dict):
    """
    Ajusta el score final según confiabilidad de fuente
    """

    trust = source_info.get("trust_level", 0.5)

    # --------------------------------------------------
    # FUENTE FUERTE → reduce riesgo
    # --------------------------------------------------
    if trust > 0.8:
        risk_score *= 0.8

    # --------------------------------------------------
    # FUENTE DÉBIL → aumenta riesgo
    # --------------------------------------------------
    elif trust < 0.4:
        risk_score *= 1.2

    # --------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------
    return max(min(risk_score, 1.0), 0.0)