# promises.py

import re
from backend.Analysis.rules_types import RuleResult

PROMISE_PATTERNS = [
    r"\bganancia segura\b",
    r"\bsin riesgo\b",
    r"\b100 ?% garantizado\b",
    r"\brendimiento garantizado\b",
    r"\bbeneficio asegurado\b"
]


def check_promises(text: str) -> RuleResult:

    result = RuleResult()

    text_lower = text.lower()

    for pattern in PROMISE_PATTERNS:

        if re.search(pattern, text_lower):

            result.points += 0.8
            result.reasons.append("exaggerated_promises")
            result.evidence.append(f"Promesa absoluta detectada: {pattern}")

            break

    return result