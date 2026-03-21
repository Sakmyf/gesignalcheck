from backend.Analysis.base import AnalysisResult


def check_narrative_patterns(text: str) -> AnalysisResult:

    result = AnalysisResult()
    lower = text.lower()

    # =========================================
    # BLOQUE 1 — CONSPIRATIVO
    # Frases específicas de narrativa de ocultamiento
    # Peso: -0.6 (alto — señal clara)
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

    conspirative_matches = [p for p in conspirative_patterns if p in lower]

    if conspirative_matches:
        result.points -= 0.6
        result.reasons.append("estructura narrativa conspirativa detectada")
        result.evidence.extend(conspirative_matches)

    # =========================================
    # BLOQUE 2 — NARRATIVA DRAMATIZADA
    # Frases de escenificación emocional — requiere 2+ coincidencias
    # Peso: -0.4 (medio)
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

    dramatized_matches = [p for p in dramatized_patterns if p in lower]

    if len(dramatized_matches) >= 2:
        result.points -= 0.4
        result.reasons.append("estructura narrativa dramatizada")
        result.evidence.extend(dramatized_matches)

    # =========================================
    # BLOQUE 3 — INDICIOS DE RECONSTRUCCIÓN
    # Señales de relato no verificable — requiere 2+ coincidencias
    # Peso: -0.5 (medio-alto)
    # =========================================

    reconstruction_clues = [
        "escena",
        "relato",
        "imaginada",
        "reconstrucción",
        "recreación",
        "versiones",
    ]

    reconstruction_matches = [p for p in reconstruction_clues if p in lower]

    if len(reconstruction_matches) >= 2:
        result.points -= 0.5
        result.reasons.append("posible reconstrucción no verificable")
        result.evidence.extend(reconstruction_matches)

    # =========================================
    # BLOQUE 4 — TONO NARRATIVO SECUENCIAL
    # Conectores genéricos — umbral alto para evitar falsos positivos
    # Peso: -0.2 (bajo — señal débil)
    # =========================================

    narrative_connectors = [
        "y aunque",
        "sin embargo",
        "entonces",
        "finalmente",
    ]

    connector_count = sum(1 for c in narrative_connectors if c in lower)

    if connector_count >= 5:
        result.points -= 0.2
        result.reasons.append("estructura narrativa secuencial")

    # =========================================
    # LIMPIEZA FINAL — dedup con orden estable
    # =========================================

    result.evidence = list(dict.fromkeys(result.evidence))
    result.reasons = list(dict.fromkeys(result.reasons))

    return result