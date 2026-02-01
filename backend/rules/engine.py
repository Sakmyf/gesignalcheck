# rules/engine.py
from rules.types import RuleResult
from rules.urgency import check_urgency
from rules.promises import check_promises
from rules.emotions import check_emotions

def analyze_text(text: str) -> RuleResult:
    score = 0.0
    evidence = []

    for fn in (check_urgency, check_promises, check_emotions):
        result = fn(text)
        score += result.score
        evidence.extend(result.evidence)

    return RuleResult(score=score, evidence=evidence)
