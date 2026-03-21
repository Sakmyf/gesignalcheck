# legacy_engine.py

from backend.Analysis.rules_types import RuleResult
from backend.Analysis.urgency import check_urgency
from backend.Analysis.promises import check_promises
from backend.Analysis.emotions import check_emotions


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
        total.evidence.extend(r.evidence)

    return total