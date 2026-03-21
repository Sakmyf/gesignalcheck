# credibility.py

import re
from backend.Analysis.rules_types import RuleResult


SOURCE_PATTERNS = [
    r"según",
    r"dijo",
    r"informó",
    r"declaró",
    r"reportó",
    r"informe",
    r"de acuerdo con",
]

DATA_PATTERNS = [
    r"\d+%",       # porcentaje
    r"\d{4}",      # años
    r"\d+\.\d+",   # decimales
]

OPINION_PATTERNS = [
    r"creo que",
    r"me parece",
    r"es evidente que",
    r"sin dudas",
]


def check_credibility(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    has_source = any(re.search(p, text_lower) for p in SOURCE_PATTERNS)
    has_data = any(re.search(p, text_lower) for p in DATA_PATTERNS)
    has_opinion = any(re.search(p, text_lower) for p in OPINION_PATTERNS)

    # 🔴 Opinión fuerte sin respaldo
    if has_opinion and not has_source and not has_data:
        result.points += 0.9
        result.reasons.append("low_credibility_opinion")
        result.evidence.append("Opinión fuerte sin fuentes ni datos")

    # 🟠 Sin fuentes detectadas
    elif not has_source:
        result.points += 0.5
        result.reasons.append("no_detected_source")
        result.evidence.append("No se detectaron fuentes claras")

    return result

def analyze(text: str):
    return check_credibility(text)