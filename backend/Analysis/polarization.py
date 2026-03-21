import re
from backend.Analysis.rules_types import RuleResult


POLARIZATION_PATTERNS = [
    r"ellos vs nosotros",
    r"la élite",
    r"el sistema",
    r"todos están en contra",
    r"los verdaderos culpables",
]

GENERALIZATION_PATTERNS = [
    r"todos",
    r"nadie",
    r"siempre",
    r"nunca",
]


def check_polarization(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    matches = 0

    for pattern in POLARIZATION_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1
            result.evidence.append(f"Patrón polarizante detectado: {pattern}")

    generalizations = sum(
        len(re.findall(g, text_lower)) for g in GENERALIZATION_PATTERNS
    )

    if matches > 0:
        result.points += min(1.0, matches * 0.3)
        result.reasons.append("polarization_detected")

    if generalizations > 3:
        result.points += 0.3
        result.reasons.append("overgeneralization")

    return result


def analyze(text: str):
    return check_polarization(text)