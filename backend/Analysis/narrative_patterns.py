# ======================================================
# SIGNALCHECK — NARRATIVE PATTERNS (v8.7 FIX)
# ======================================================

def analyze(text: str):

    lower = text.lower()

    score = 0.0
    reasons = []
    evidence = []

    # =========================================
    # BLOQUE 1 — CONSPIRATIVO
    # =========================================

    conspirative_patterns = [
        "lo que no quieren que sepas",
        "la verdad que nadie dice",
        "esto no te lo van a mostrar",
        "los medios lo ocultan",
        "compartí antes que lo borren",
        "esto será eliminado",
        "los poderosos no quieren",
        "te están mintiendo",
        "la verdad oculta",
        "nadie habla de esto",
    ]

    matches = [p for p in conspirative_patterns if p in lower]

    if matches:
        score += 0.6
        reasons.append("conspiracy_narrative")
        evidence.extend(matches)

    # =========================================
    # BLOQUE 2 — DRAMATIZACIÓN
    # =========================================

    dramatized_patterns = [
        "escena imaginada",
        "recreación",
        "según versiones",
        "tras la carrera",
        "lo que parecía",
        "se volvió",
        "ola imparable",
        "cargada de",
        "incapaz de",
    ]

    matches = [p for p in dramatized_patterns if p in lower]

    if len(matches) >= 2:
        score += 0.4
        reasons.append("dramatized_structure")
        evidence.extend(matches)

    # =========================================
    # BLOQUE 3 — RECONSTRUCCIÓN
    # =========================================

    reconstruction_clues = [
        "escena",
        "relato",
        "imaginada",
        "reconstrucción",
        "recreación",
        "versiones",
    ]

    matches = [p for p in reconstruction_clues if p in lower]

    if len(matches) >= 2:
        score += 0.5
        reasons.append("unverified_reconstruction")
        evidence.extend(matches)

    # =========================================
    # BLOQUE 4 — CONECTORES NARRATIVOS
    # =========================================

    narrative_connectors = [
        "y aunque",
        "sin embargo",
        "entonces",
        "finalmente",
    ]

    connector_count = sum(1 for c in narrative_connectors if c in lower)

    if connector_count >= 5:
        score += 0.2
        reasons.append("narrative_sequence")

    # =========================================
    # LIMPIEZA FINAL
    # =========================================

    evidence = list(dict.fromkeys(evidence))
    reasons = list(dict.fromkeys(reasons))

    return {
        "score": round(score, 2),
        "reasons": reasons,
        "evidence": evidence
    }