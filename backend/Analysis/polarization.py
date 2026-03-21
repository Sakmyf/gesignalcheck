# polarization.py

import re
from backend.Analysis.rules_types import RuleResult


POLARIZATION_PATTERNS = [
    r"ellos contra nosotros",
    r"nos quieren destruir",
    r"son todos iguales",
    r"siempre mienten",
    r"nunca dicen la verdad",
    r"la única solución es",
    r"están arruinando el país",
    r"no les importa la gente",
]


GENERALIZATION_PATTERNS = [
    r"\btodos\b",
    r"\bnadie\b",
    r"\bsiempre\b",
    r"\bnunca\b",
]


def check_polarization(text: str) -> RuleResult:

    result = RuleResult()

    text_lower = text.lower()

    matches = 0

    for pattern in POLARIZATION_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1
            result.evidence.append(f"Patrón polarizante detectado: {pattern}")

    generalizations = sum(len(re.findall(g, text_lower)) for g in GENERALIZATION_PATTERNS)

    # Polarización leve
    if matches == 1:
        result.points += 0.4
        result.reasons.append("polarization_detected")

    # Polarización fuerte
    elif matches >= 2:
        result.points += 0.8
        result.reasons.append("strong_polarization")

    # Generalizaciones absolutas reiteradas
    if generalizations >= 3:
        result.points += 0.4
        result.reasons.append("absolute_generalizations")
        result.evidence.append("Uso reiterado de generalizaciones absolutas")

    return result