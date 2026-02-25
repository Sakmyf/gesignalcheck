# promises.py
import re
from backend.Analysis.rules_types import RuleResult

PROMISES = r"(ganancia segura|sin riesgo|100% garantizado)"

def check_promises(text: str) -> RuleResult:

    result = RuleResult()

    if re.search(PROMISES, text, re.I):
        result.points += 0.8
        result.reasons.append("exaggerated_promises")
        result.evidence.append("Promesas irreales o garantizadas detectadas")

    return result