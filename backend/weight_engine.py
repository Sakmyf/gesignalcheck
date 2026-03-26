# ======================================================
# SIGNALCHECK – WEIGHT ENGINE v2.0
# Ajuste dinámico de pesos según contexto y fuente.
# Keys alineadas a BASE_WEIGHTS del engine v12.
# ======================================================

def adjust_weights(base_weights: dict, context: str, source_info: dict) -> dict:

    weights = base_weights.copy()
    trust = source_info.get("trust_level", 0.55)

    # --------------------------------------------------
    # CONTEXTO: SALUD / CIENCIA
    # --------------------------------------------------
    if context == "health_science":
        weights["scientific_claims"] = weights.get("scientific_claims", 0.08) * 1.5
        weights["authority"]         = weights.get("authority", 0.10)         * 1.3
        weights["emotions"]          = weights.get("emotions", 0.12)          * 0.7

    # --------------------------------------------------
    # CONTEXTO: POLÍTICA
    # --------------------------------------------------
    elif context == "politics":
        weights["polarization"]   = weights.get("polarization", 0.12)   * 1.4
        weights["misinformation"] = weights.get("misinformation", 0.10) * 1.2
        weights["emotions"]       = weights.get("emotions", 0.12)        * 1.1

    # --------------------------------------------------
    # CONTEXTO: OPINIÓN
    # --------------------------------------------------
    elif context == "opinion":
        weights["emotions"]     = weights.get("emotions", 0.12)     * 0.6
        weights["polarization"] = weights.get("polarization", 0.12) * 0.7

    # --------------------------------------------------
    # CONTEXTO: NOTICIAS
    # --------------------------------------------------
    elif context == "news":
        weights["credibility"] = weights.get("credibility", 0.15) * 0.7

    # --------------------------------------------------
    # AJUSTE POR FUENTE
    # --------------------------------------------------
    if trust > 0.8:
        weights["credibility"]    = weights.get("credibility", 0.15)    * 0.6
        weights["misinformation"] = weights.get("misinformation", 0.10) * 0.7

    elif trust < 0.4:
        weights["credibility"]    = weights.get("credibility", 0.15)    * 1.3
        weights["misinformation"] = weights.get("misinformation", 0.10) * 1.3
        weights["hypothetical"]   = weights.get("hypothetical", 0.05)   * 1.2

    return weights