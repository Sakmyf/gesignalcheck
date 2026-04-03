import re
from backend.Analysis.rules_types import RuleResult


MEDICAL_KEYWORDS = [
    # español
    r"\bcura\b",
    r"\bcurar\b",
    r"tratamiento definitivo",
    r"100 ?% efectivo",
    r"comprobado científicamente",
    r"reemplaza la medicina",
    r"la medicina no quiere que sepas",
    r"avalado por médicos",
    r"científicamente probado",
    r"sin efectos secundarios",
    r"cura definitiva",
    # inglés
    r"\bcure[sd]?\b",
    r"100 ?% effective",
    r"scientifically (proven|backed|validated)",
    r"science.?backed",
    r"clinically proven",
    r"doctors (don.?t want|hate)",
    r"(extend|reverse|stop) aging",
    r"live (longer|forever|your longest)",
    r"longevity (revolution|breakthrough|secret)",
    r"beyond today.?s limits",
    r"(eliminate|defeat|beat) (cancer|disease|aging)",
    r"miracle (cure|solution|treatment)",
    r"breakthrough (discovery|treatment|cure)",
]

SUPPORT_INDICATORS = [
    # español
    "estudio",
    "ensayo clínico",
    "universidad",
    "revista científica",
    "publicado en",
    "journal",
    "investigación",
    # inglés
    "study",
    "clinical trial",
    "university",
    "published in",
    "research",
    "peer.reviewed",
    "according to",
    "harvard",
    "mit",
    "nih",
    "who",
]


def check_scientific_claims(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    claim_matches = []
    for pattern in MEDICAL_KEYWORDS:
        if re.search(pattern, text_lower):
            claim_matches.append(pattern)

    if claim_matches:
        has_support = any(re.search(ind, text_lower) for ind in SUPPORT_INDICATORS)

        if not has_support:
            # Escalar según cantidad de claims sin respaldo
            result.points += min(0.7 + (len(claim_matches) - 1) * 0.1, 1.0)
            result.reasons.append("unsupported_scientific_claim")
            result.evidence.append(
                f"Afirmación científica/salud sin respaldo ({len(claim_matches)} señales)"
            )
        else:
            # Tiene respaldo pero igual suma algo si hay muchas claims
            if len(claim_matches) >= 3:
                result.points += 0.2
                result.reasons.append("multiple_health_claims_with_partial_support")

    return result


def analyze(text: str):
    return check_scientific_claims(text)