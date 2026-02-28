class AnalysisResult:
    def __init__(self):
        self.points = 0.0
        self.reasons = []
        self.evidence = []


def check_scientific_claims(text: str):

    result = AnalysisResult()
    lower = text.lower()

    # Palabras asociadas a afirmaciones médicas fuertes
    medical_keywords = [
        "cura", "curar", "tratamiento definitivo",
        "100% efectivo", "comprobado científicamente",
        "reemplaza la medicina", "la medicina no quiere que sepas",
        "avalado por médicos", "científicamente probado"
    ]

    # Indicadores de respaldo científico
    support_indicators = [
        "estudio", "ensayo clínico",
        "universidad", "revista científica",
        "publicado en", "journal",
        "investigación"
    ]

    found_claim = False
    for word in medical_keywords:
        if word in lower:
            found_claim = True
            result.evidence.append(word)

    if found_claim:

        has_support = any(indicator in lower for indicator in support_indicators)

        if not has_support:
            result.points -= 0.6
            result.reasons.append(
                "Afirmación médica o científica sin respaldo verificable detectado"
            )

    return result