# engine.py
from rules_types import RuleResult
from urgency import check_urgency
from promises import check_promises
from emotions import check_emotions

def analyze_text(text: str) -> RuleResult:
    results = [
        check_urgency(text),
        check_promises(text),
        check_emotions(text),
    ]

    total = RuleResult()

    for r in results:
        total.points += r.points
        total.reasons.extend(r.reasons)
        if r.critical:
            total.critical = True

    return total
