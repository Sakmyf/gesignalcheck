class AnalysisResult:
    def __init__(self, points=0.0, reasons=None, evidence=None):
        self.points = points
        self.reasons = reasons or []
        self.evidence = evidence or []


def adapt_dict_to_result(data, weight=1.0, reason_prefix=""):
    """
    Convierte dict → AnalysisResult
    Mantiene coherencia con engine existente
    """

    score = data.get("score") or data.get("gap_score") or 0.0
    signals = data.get("signals", [])

    # reasons legibles
    reasons = [f"{reason_prefix}{s}" for s in signals]

    # points negativos = riesgo (como tus módulos actuales)
    points = -score * weight

    return AnalysisResult(
        points=points,
        reasons=reasons,
        evidence=signals
    )