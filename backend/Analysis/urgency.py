import re
from backend.Analysis.rules_types import RuleResult


URGENCY_PATTERNS = [
    r"\burgente\b",
    r"última oportunidad",
    r"actu[aá] ahora",
    r"inmediato",
    r"antes de que lo borren",
    r"compart[ií] antes que lo eliminen",
]


def check_urgency(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    matches = 0

    for pattern in URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 1

    if matches >= 1:
        score = min(0.8, matches * 0.3)

        result.points += score
        result.reasons.append("urgency_pressure")
        result.evidence.append(f"Urgency patterns detected ({matches})")

    return result


def analyze(text: str):
    return check_urgency(text)