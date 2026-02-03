# urgency.py
from types import RuleResult

def check_urgency(text: str) -> RuleResult:
    score = 0.0
    evidence = []

    if "urgente" in text.lower():
        score += 0.2
        evidence.append("Lenguaje de urgencia detectado")

    return RuleResult(score=score, evidence=evidence)
