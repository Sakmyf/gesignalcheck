# ======================================================
# SIGNALCHECK — NARRATIVE PATTERNS (v8.8)
# FIX: Score de reconstrucción ficticia + peso combinado
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
        # inglés
        "imagined scene",
        "recreation",
        "as if",
        "could have",
        "would have said",
    ]

    matches_drama = [p for p in dramatized_patterns if p in lower]

    if len(matches_drama) >= 2:
        score += 0.5  # era 0.4
        reasons.append("dramatized_structure")
        evidence.extend(matches_drama)

    # =========================================
    # BLOQUE 3 — RECONSTRUCCIÓN FICTICIA
    # =========================================

    reconstruction_clues = [
        "escena",
        "relato",
        "imaginada",
        "reconstrucción",
        "recreación",
        "versiones",
        "ficción",
        "ficticio",
        "narrativa",
        "según la recreación",
    ]

    matches_rec = [p for p in reconstruction_clues if p in lower]

    if len(matches_rec) >= 2:
        score += 0.6  # era 0.5
        reasons.append("unverified_reconstruction")
        evidence.extend(matches_rec)

    # =========================================
    # BLOQUE 4 — BOOST: FICCIÓN + PERSONA REAL
    # Si hay reconstrucción Y dramatización juntas → señal fuerte
    # =========================================

    if "dramatized_structure" in reasons and "unverified_reconstruction" in reasons:
        score += 0.3
        reasons.append("fictional_narrative_with_real_context")

    # =========================================
    # BLOQUE 5 — CONECTORES NARRATIVOS
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