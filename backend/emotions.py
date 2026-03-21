# ======================================================
# EMOTIONS MODULE — ADAPTADO A ENGINE v8.7
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

    for p in EMOTION_PATTERNS:
        if re.search(p, text, re.I):
            result.points -= 0.15
            result.reasons.append("manipulación emocional")
            result.evidence.append(p)

    return result