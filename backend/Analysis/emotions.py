# emotions.py
import re
from backend.Analysis.rules_types import RuleResult

EMOTION_PATTERNS = [
    r"indignación",
    r"furia",
    r"caos",
    r"paralizada",
    r"ataque",
    r"escándalo",
    r"urgente",
    r"explosión",
    r"estalló",
    r"imparable",
    r"terrible",
    r"alarmante",
    r"no vuelvas a",
]

def check_emotions(text: str) -> RuleResult:

    result = RuleResult()

    matches = 0

    for p in EMOTION_PATTERNS:
        if re.search(p, text, re.I):
            matches += 1

    if matches >= 1:
        # Escala leve, no exagerada
        result.points += min(1.0, matches * 0.2)
        result.reasons.append("emotional_intensity")
        result.evidence.append("Narrativa emocional intensa")

    return result