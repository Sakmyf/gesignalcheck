# polarization.py
import re
from .rules_types import RuleResult

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

    matches = 0

    for p in POLARIZATION_PATTERNS:
        if re.search(p, text, re.I):
            matches += 1

    generalizations = 0
    for g in GENERALIZATION_PATTERNS:
        generalizations += len(re.findall(g, text, re.I))

    score = 0.0
    reasons = []
    evidence = []

    # Polarización leve
    if matches == 1:
        score = -0.1
        reasons.append("polarization_detected")
        evidence.append("Lenguaje polarizante leve")

    # Polarización fuerte
    elif matches >= 2:
        score = -0.25
        reasons.append("strong_polarization")
        evidence.append("Narrativa de confrontación reiterada")

    # Generalizaciones absolutas reiteradas
    if generalizations >= 3:
        score -= 0.1
        reasons.append("absolute_generalizations")
        evidence.append("Uso reiterado de generalizaciones absolutas")

    return RuleResult(
        points=score,
        reasons=reasons,
        evidence=evidence
    )