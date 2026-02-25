# urgency.py
import re
from backend.Analysis.rules_types import RuleResult

URGENCY_PATTERNS = [
    r"urgente",
    r"última oportunidad",
    r"actuá ahora",
    r"inmediato",
    r"antes de que lo borren",
    r"compartí antes que lo eliminen",
]

def check_urgency(text: str) -> RuleResult:

    result = RuleResult()

    matches = 0

    for p in URGENCY_PATTERNS:
        if re.search(p, text, re.I):
            matches += 1

    if matches >= 1:
        result.points += min(0.8, matches * 0.3)
        result.reasons.append("urgency_pressure")
        result.evidence.append("Lenguaje de presión temporal detectado")

    return result