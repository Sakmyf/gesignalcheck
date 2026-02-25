print("ENGINE RULE ENGINE 4.0 ACTIVO")

from backend.Analysis.emotions import check_emotions
from backend.Analysis.credibility import check_credibility
from backend.Analysis.misinformation import check_misinformation
from backend.Analysis.structural import check_structural
from backend.Analysis.urgency import check_urgency
from backend.Analysis.promises import check_promises
from backend.Analysis.rules_types import RuleResult
from urllib.parse import urlparse


MAX_SCORE = 8.0  # techo teórico ajustable


def detect_site_type(url: str) -> str:
    if not url:
        return "unknown"

    domain = urlparse(url).netloc.lower()

    if any(k in domain for k in [".gob.", ".gov.", ".edu."]):
        return "institutional"

    if any(k in domain for k in ["clarin", "bbc", "cnn", "reuters"]):
        return "media"

    if any(k in domain for k in ["facebook", "instagram", "tiktok", "x.com"]):
        return "social"

    return "blog"


def analyze_context(text: str, url: str = ""):

    site_type = detect_site_type(url)

    total = RuleResult()

    modules = [
        check_emotions,
        check_credibility,
        check_misinformation,
        check_structural,
        check_urgency,
        check_promises,
    ]

    for module in modules:
        result = module(text)
        total.merge(result)

    raw_score = total.points

    # Ajuste por tipo de sitio
    if site_type == "institutional":
        raw_score *= 0.7
    elif site_type == "media":
        raw_score *= 0.9
    elif site_type == "social":
        raw_score *= 1.1

    # Normalización 0–1
    normalized_score = raw_score / MAX_SCORE
    normalized_score = max(min(normalized_score, 1.0), 0.0)

    # Decisión final
    if normalized_score < 0.25:
        status = "green"
        label = "contenido informativo"
    elif normalized_score < 0.55:
        status = "yellow"
        label = "requiere lectura crítica"
    else:
        status = "red"
        label = "información cuestionable"

    return {
        "status": status,
        "label": label,
        "score": round(normalized_score, 2),
        "signals": total.evidence,
        "reasons": total.reasons,
        "site_type": site_type,
        "raw_score": round(raw_score, 2)
    }