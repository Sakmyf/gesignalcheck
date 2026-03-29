import re
from backend.Analysis.rules_types import RuleResult

# 🔥 FIX: Pasamos de palabras sueltas ("urgente", "inmediato") a patrones de presión
URGENCY_PATTERNS = [
    r"última oportunidad",
    r"actu[aá] ahora",
    r"antes (de )?que lo borren",
    r"compart[ií] antes que lo eliminen",
    r"solo\s+por\s+hoy",
    r"tiempo\s+limitado",
    r"oferta\s+(termina|finaliza)",
    r"decisión\s+inmediata" 
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
        result.evidence.append(f"Patrones de urgencia detectados ({matches})")

    return result

def analyze(text: str):
    return check_urgency(text)