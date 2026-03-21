# ======================================================
# SIGNALCHECK — URGENCY MODULE (ADAPTADO v8.7)
# ======================================================

import re
from backend.Analysis.base import AnalysisResult


URGENCY_PATTERNS = r"(urgente|última oportunidad|actuá ahora|inmediato)"


def analyze(text: str) -> AnalysisResult:

    result = AnalysisResult()

    matches = re.findall(URGENCY_PATTERNS, text, re.I)

    if matches:
        result.points -= 0.3
        result.reasons.append("presión de urgencia")
        result.evidence.extend(matches)

    return result