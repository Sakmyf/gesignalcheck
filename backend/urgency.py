# urgency.py

import re
from rules_types import RuleResult

URGENCY_PATTERNS = r"(urgente|última oportunidad|actuá ahora|inmediato|no te lo pierdas|ahora o nunca|antes de que sea tarde|aprovechá ya|solo hoy|tiempo limitado)"

def check_urgency(text: str) -> RuleResult:

    matches = re.findall(URGENCY_PATTERNS, text, re.I)

    if matches:
        intensity = len(matches)

        # Escalado progresivo (MUY importante)
        if intensity >= 3:
            points = -0.7
        elif intensity == 2:
            points = -0.5
        else:
            points = -0.3

        return RuleResult(
            points=points,
            reasons=["urgency_pressure"],
            evidence=[f"Lenguaje de urgencia detectado ({intensity})"]
        )

    return RuleResult()