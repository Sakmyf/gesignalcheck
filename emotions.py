# ======================================================
# SIGNALCHECK — EMOTIONS MODULE (ADAPTADO v8.7)
# ======================================================

import re
from backend.Analysis.base import AnalysisResult


EMOTION_PATTERNS = [
    r"cansado de",
    r"merecés",
    r"tu vida va a cambiar",
    r"libertad financiera",
    r"viví como soñás",
]


def analyze(text: str) -> AnalysisResult:

    result = AnalysisResult()

    matches = []

    for p in EMOTION_PATTERNS:
        found = re.findall(p, text, re.I)
        if found:
            matches.extend(found)

    if matches:
        result.points -= 0.15
        result.reasons.append("manipulación emocional")
        result.evidence.extend(matches)

    return result