# ======================================================
# SIGNALCHECK – NARRATIVE PROFILE v1.1 (ALINEADO)
# ======================================================

def build_narrative_profile(signals: list, risk_score: float):
    """
    Construye un perfil interpretativo basado en señales reales del engine
    """

    s = set(signals)

    profile = {
        "emocionalidad": 0.0,
        "manipulacion": 0.0,
        "confiabilidad": 1.0,
        "claridad": 1.0
    }

    # --------------------------------------------------
    # EMOCIONALIDAD
    # --------------------------------------------------
    if "emotional_intensity" in s:
        profile["emocionalidad"] += 0.5

    if "urgency_pressure" in s:
        profile["emocionalidad"] += 0.3

    if "polarization_detected" in s:
        profile["emocionalidad"] += 0.3

    # --------------------------------------------------
    # MANIPULACIÓN
    # --------------------------------------------------
    if "unsupported_scientific_claim" in s:
        profile["manipulacion"] += 0.4

    if "exaggerated_promises" in s:
        profile["manipulacion"] += 0.3

    if "low_credibility_opinion" in s:
        profile["manipulacion"] += 0.3

    if "overgeneralization" in s:
        profile["manipulacion"] += 0.2

    # --------------------------------------------------
    # CONFIABILIDAD (inverso)
    # --------------------------------------------------
    if "unsupported_scientific_claim" in s:
        profile["confiabilidad"] -= 0.4

    if "low_credibility_opinion" in s:
        profile["confiabilidad"] -= 0.3

    if "hypothetical_or_unverified_claim" in s:
        profile["confiabilidad"] -= 0.3

    # --------------------------------------------------
    # CLARIDAD
    # --------------------------------------------------
    if "clickbait_structure" in s:
        profile["claridad"] -= 0.3

    if "absolute_generalization" in s:
        profile["claridad"] -= 0.3

    # --------------------------------------------------
    # NORMALIZACIÓN (0 a 1)
    # --------------------------------------------------
    for key in profile:
        profile[key] = max(min(profile[key], 1.0), 0.0)

    # --------------------------------------------------
    # AJUSTE POR RIESGO GLOBAL
    # --------------------------------------------------
    if risk_score > 0.7:
        profile["confiabilidad"] *= 0.7

    return profile