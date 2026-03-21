import re
from backend.Analysis.rules_types import RuleResult


MEDICAL_KEYWORDS = [
    r"\bcura\b",
    r"\bcurar\b",
    r"tratamiento definitivo",
    r"100 ?% efectivo",
    r"comprobado científicamente",
    r"reemplaza la medicina",
    r"la medicina no quiere que sepas",
    r"avalado por médicos",
    r"científicamente probado"
]

SUPPORT_INDICATORS = [
    "estudio",
    "ensayo clínico",
    "universidad",
    "revista científica",
    "publicado en",
    "journal",
    "investigación"
]


def check_scientific_claims(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    claim_matches = []

    for pattern in MEDICAL_KEYWORDS:
        if re.search(pattern, text_lower):
            claim_matches.append(pattern)

    if claim_matches:

        has_support = any(indicator in text_lower for indicator in SUPPORT_INDICATORS)

        if not has_support:
            result.points += 0.7
            result.reasons.append("unsupported_scientific_claim")
            result.evidence.append(
                "Afirmación científica fuerte sin respaldo detectado"
            )

    return result


def analyze(text: str):
    return check_scientific_claims(text)