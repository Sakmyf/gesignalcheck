class AnalysisResult:
    def __init__(self):
        self.points = 0.0
        self.reasons = []
        self.evidence = []


def check_hypothetical(text: str):

    result = AnalysisResult()
    lower = text.lower()

    hypothetical_patterns = [
        "habría dicho",
        "habría ocurrido",
        "según trascendió",
        "se comenta que",
        "escena imaginada",
        "fuentes cercanas",
        "todo indicaría",
        "aparentemente"
    ]

    matches = [p for p in hypothetical_patterns if p in lower]

    if matches:
        result.points -= 0.4
        result.reasons.append(
            "Contenido narrativo no verificable o hipotético detectado"
        )
        result.evidence.extend(matches)

    return result