import re
from backend.Analysis.rules_types import RuleResult


PROMISE_PATTERNS = [
    # español
    r"\bganancia segura\b",
    r"\bsin riesgo\b",
    r"\b100 ?% garantizado\b",
    r"\brendimiento garantizado\b",
    r"\bbeneficio asegurado\b",
    r"\brezultados garantizados\b",
    r"\béxito garantizado\b",
    r"\bsin esfuerzo\b",
    r"\bvida eterna\b",
    r"\bcura definitiva\b",
    # inglés
    r"\bguaranteed results?\b",
    r"\bno risk\b",
    r"\brisk.?free\b",
    r"\b100 ?% guaranteed\b",
    r"\bguaranteed (income|profit|return|benefit)\b",
    r"\blive (longer|forever|your longest)\b",
    r"\bextend(ing)? (your |human )?life\b",
    r"\bbeyond today.?s limits?\b",
    r"\blongevity revolution\b",
    r"\breverse aging\b",
    r"\banti.?aging (breakthrough|solution|cure)\b",
    r"\bscience.?backed (health|life|longevity)\b",
    r"\bunlock (your|the) (potential|secret|truth)\b",
]


def check_promises(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    matched = []
    for pattern in PROMISE_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(pattern)

    if matched:
        # Más de una promesa extraordinaria = señal más fuerte
        result.points += min(0.8 + (len(matched) - 1) * 0.1, 1.0)
        result.reasons.append("exaggerated_promises")
        result.evidence.append(f"Promesa absoluta detectada ({len(matched)} señales)")

    return result


def analyze(text: str):
    return check_promises(text)