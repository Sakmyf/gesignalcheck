# ======================================================
# SIGNALCHECK — PROMISES MODULE (ADAPTADO v8.7)
# ======================================================

import re
from backend.Analysis.base import AnalysisResult


PROMISES = r"(ganancia segura|sin riesgo|100% garantizado)"


def analyze(text: str) -> AnalysisResult:

    result = AnalysisResult()

    matches = re.findall(PROMISES, text, re.I)

    if matches:
        result.points -= 0.4
        result.reasons.append("promesas exageradas o irreales")
        result.evidence.extend(matches)

    return result