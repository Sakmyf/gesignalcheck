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
    r"explosión",
    r"estalló",
    r"imparable",
    r"terrible",
    r"alarmante",
    r"no vuelvas a",
]


def check_emotions(text: str) -> RuleResult:

    result = RuleResult()

    text_lower = text.lower()

    matches = [p for p in EMOTION_PATTERNS if re.search(p, text_lower)]

    if matches:

        score = min(1.0, len(matches) * 0.2)

        result.points += score
        result.reasons.append("emotional_intensity")
        result.evidence.append(
            f"Lenguaje emocional detectado ({len(matches)} señales)"
        )

    return result