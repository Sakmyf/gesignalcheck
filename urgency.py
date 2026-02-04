# urgency.py
import re
from rules_types import RuleResult

URGENCY_PATTERNS = r"(urgente|última oportunidad|actuá ahora|inmediato)"

def check_urgency(text: str) -> RuleResult:
    if re.search(URGENCY_PATTERNS, text, re.I):
        return RuleResult(
            points=-0.3,
            reasons=["urgency_pressure"],
            evidence=["Lenguaje de urgencia detectado"]
        )
    return RuleResult()
