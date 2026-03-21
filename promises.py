# promises.py
import re
from rules_types import RuleResult

PROMISES = r"(ganancia segura|sin riesgo|100% garantizado)"

def check_promises(text: str) -> RuleResult:
    if re.search(PROMISES, text, re.I):
        return RuleResult(
            points=-0.4,
            reasons=["exaggerated_promises"],
            evidence=["Promesas irreales o garantizadas"]
        )
    return RuleResult()
