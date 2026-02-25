
# misinformation.py
import re
from backend.Analysis.rules_types import RuleResult


SERIOUS_CLAIMS = [
    r"fraude",
    r"estafa",
    r"corrupción",
    r"manipulación",
    r"engaño",
    r"ilegal",
]

CONSPIRACY_PATTERNS = [
    r"no quieren que sepas",
    r"te están ocultando",
    r"nadie habla de",
    r"verdad oculta",
]

CATEGORICAL_PATTERNS = [
    r"es un hecho",
    r"está probado",
    r"sin dudas",
    r"queda demostrado",
]


ATTRIBUTION_PATTERNS = [
    r"según",
    r"dijo",
    r"informó",
    r"declaró",
    r"reportó",
    r"informe",
    r"de acuerdo con",
]


def check_misinformation(text: str) -> RuleResult:

    result = RuleResult()

    # 🔴 Acusaciones graves sin atribución
    for claim in SERIOUS_CLAIMS:
        if re.search(claim, text, re.I):
            if not any(re.search(a, text, re.I) for a in ATTRIBUTION_PATTERNS):
                result.points += 1.2
                result.reasons.append("serious_accusation_without_source")
                result.evidence.append("Acusación grave sin fuente atribuida")

    # 🟠 Lenguaje conspirativo
    for pattern in CONSPIRACY_PATTERNS:
        if re.search(pattern, text, re.I):
            result.points += 1.0
            result.reasons.append("conspiracy_language")
            result.evidence.append("Lenguaje conspirativo detectado")

    # 🟡 Afirmaciones categóricas fuertes
    for pattern in CATEGORICAL_PATTERNS:
        if re.search(pattern, text, re.I):
            result.points += 0.7
            result.reasons.append("categorical_claim")
            result.evidence.append("Afirmación categórica fuerte")

    return result