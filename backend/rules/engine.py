from typing import List

from .urgency import check_urgency
from .promises import check_promises
from .emotions import check_emotions


class RuleResult:
    def __init__(self, score: float = 0.0, evidence: List[str] = None):
        self.score = score
        self.evidence = evidence or []

    def merge(self, other: "RuleResult"):
        self.score += other.score
        self.evidence.extend(other.evidence)


def analyze_text(text: str) -> RuleResult:
    result = RuleResult()

    for rule in (check_urgency, check_promises, check_emotions):
        result.merge(rule(text))

    if (
        "urgency_language" in result.evidence
        and "exaggerated_promises" in result.evidence
    ):
        result.score += 0.10
        result.evidence.append("high_risk_combination")

    return result

