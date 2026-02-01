import re
from .engine import RuleResult

URGENCY_PATTERNS = [
    r"última oportunidad",
    r"por tiempo limitado",
    r"solo hoy",
    r"ahora",
    r"no te quedes afuera",
    r"quedan pocas",
]

def check_urgency(text: str) -> RuleResult:
    for p in URGENCY_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return RuleResult(0.15, ["urgency_language"])
    return RuleResult()
