# emotions.py
import re
from rules_types import RuleResult

EMOTION_PATTERNS = [
    r"cansado de",
    r"merecés",
    r"tu vida va a cambiar",
    r"libertad financiera",
    r"viví como soñás",
]

def check_emotions(text: str) -> RuleResult:
    for p in EMOTION_PATTERNS:
        if re.search(p, text, re.I):
            return RuleResult(
                points=-0.15,
                reasons=["emotional_manipulation"],
                evidence=["Lenguaje emocional persuasivo"]
            )
    return RuleResult()
