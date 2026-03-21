# ======================================================
# SIGNALCHECK – NARRATIVE PROFILE v1.0
# ======================================================

def build_narrative_profile(signals: list, risk_score: float):
    """
    Construye un perfil interpretativo del contenido
    basado en señales detectadas
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
    if "emotional_language" in s:
        profile["emocionalidad"] += 0.5

    if "urgency_language" in s:
        profile["emocionalidad"] += 0.3

    if "polarized_language" in s:
        profile["emocionalidad"] += 0.3

    # --------------------------------------------------
    # MANIPULACIÓN
    # --------------------------------------------------
    if "lack_of_evidence" in s:
        profile["manipulacion"] += 0.4

    if "exaggerated_promises" in s:
        profile["manipulacion"] += 0.3

    if "headline_exaggeration" in s:
        profile["manipulacion"] += 0.3

    if "weak_authority" in s:
        profile["manipulacion"] += 0.2

    # --------------------------------------------------
    # CONFIABILIDAD (inverso)
    # --------------------------------------------------
    if "lack_of_evidence" in s:
        profile["confiabilidad"] -= 0.4

    if "weak_authority" in s:
        profile["confiabilidad"] -= 0.3

    if "internal_contradiction" in s:
        profile["confiabilidad"] -= 0.3

    # --------------------------------------------------
    # CLARIDAD
    # --------------------------------------------------
    if "structural_issues" in s:
        profile["claridad"] -= 0.3

    if "content_mismatch" in s:
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