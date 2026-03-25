# ======================================================
# SIGNALCHECK – WEIGHT ENGINE v1.0
# Ajuste dinámico de pesos según contexto y fuente
# ======================================================

def adjust_weights(base_weights: dict, context: str, source_info: dict):
    """
    Ajusta los pesos de los módulos según:
    - contexto del contenido
    - confiabilidad de la fuente
    """

    weights = base_weights.copy()

    trust = source_info.get("trust_level", 0.5)

    # --------------------------------------------------
    # CONTEXTO: SALUD / CIENCIA
    # --------------------------------------------------
    if context == "health_science":
        weights["evidence"] *= 1.3
        weights["authority"] *= 1.2
        weights["emotions"] *= 0.8

    # --------------------------------------------------
    # CONTEXTO: POLÍTICA
    # --------------------------------------------------
    elif context == "politics":
        weights["polarization"] *= 1.4
        weights["emotions"] *= 1.2

    # --------------------------------------------------
    # CONTEXTO: OPINIÓN
    # --------------------------------------------------
    elif context == "opinion":
        weights["emotions"] *= 0.7
        weights["polarization"] *= 0.8

    # --------------------------------------------------
    # AJUSTE POR FUENTE
    # --------------------------------------------------
    if trust > 0.8:
        weights["credibility"] *= 0.7
        weights["misinformation"] *= 0.8

    elif trust < 0.4:
        weights["credibility"] *= 1.3
        weights["misinformation"] *= 1.2
        weights["evidence"] *= 1.2

    return weights