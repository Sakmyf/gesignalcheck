import re
from .engine import RuleResult

EMOTION_PATTERNS = [
    r"cansado de",
    r"merecés",
    r"tu vida va a cambiar",
    r"libertad financiera",
    r"viví como soñás",
]

def check_emotions(text: str) -> RuleResult:
    for p in EMOTION_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return RuleResult(0.15, ["emotional_manipulation"])
    return RuleResult()
