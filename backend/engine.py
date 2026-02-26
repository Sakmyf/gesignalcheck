print("ENGINE RULE ENGINE 5.0 ACTIVO")
print("🔥 ENGINE.PY ACTIVO")

from backend.Analysis.emotions import check_emotions
from backend.Analysis.credibility import check_credibility
from backend.Analysis.misinformation import check_misinformation
from backend.Analysis.structural import check_structural
from backend.Analysis.urgency import check_urgency
from backend.Analysis.promises import check_promises
from backend.Analysis.polarization import check_polarization
from backend.Analysis.rules_types import RuleResult
from urllib.parse import urlparse


# Techo teórico separado
MAX_QUALITY_SCORE = 4.0
MAX_RISK_SCORE = 6.0


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

    print("🧠 ANALYZE_CONTEXT EJECUTADO")

    site_type = detect_site_type(url)

    # ===============================
    # Ejecutamos módulos
    # ===============================

    emotions = check_emotions(text)
    credibility = check_credibility(text)
    misinformation = check_misinformation(text)
    structural = check_structural(text)
    urgency = check_urgency(text)
    promises = check_promises(text)
    polarization = check_polarization(text)

    # ===============================
    # QUALITY (suma positiva)
    # ===============================

    quality_points = 0.0
    quality_points += max(credibility.points, 0)
    quality_points += max(structural.points, 0)

    # ===============================
    # RISK (magnitud de negativos)
    # ===============================

    risk_points = 0.0
    risk_points += abs(min(emotions.points, 0))
    risk_points += abs(min(misinformation.points, 0))
    risk_points += abs(min(urgency.points, 0))
    risk_points += abs(min(promises.points, 0))
    risk_points += abs(min(polarization.points, 0))

    # ===============================
    # Ajuste por tipo de sitio
    # ===============================

    if site_type == "institutional":
        risk_points *= 0.7
    elif site_type == "media":
        risk_points *= 0.9
    elif site_type == "social":
        risk_points *= 1.1

    # ===============================
    # Normalización
    # ===============================

    quality_score = quality_points / MAX_QUALITY_SCORE
    quality_score = max(min(quality_score, 1.0), 0.0)

    risk_score = risk_points / MAX_RISK_SCORE
    risk_score = max(min(risk_score, 1.0), 0.0)

    # ===============================
    # Score global (para FREE)
    # ===============================

    # Riesgo pesa más que calidad
    global_score = (risk_score * 0.6) + ((1 - quality_score) * 0.4)

    # ===============================
    # Decisión visual FREE
    # ===============================

    if global_score < 0.25:
        status = "green"
        label = "contenido informativo"
    elif global_score < 0.55:
        status = "yellow"
        label = "requiere lectura crítica"
    else:
        status = "red"
        label = "información cuestionable"

    # ===============================
    # Recolección de señales
    # ===============================

    all_reasons = (
        emotions.reasons +
        credibility.reasons +
        misinformation.reasons +
        structural.reasons +
        urgency.reasons +
        promises.reasons +
        polarization.reasons
    )

    all_evidence = (
        emotions.evidence +
        credibility.evidence +
        misinformation.evidence +
        structural.evidence +
        urgency.evidence +
        promises.evidence +
        polarization.evidence
    )

    return {
        "status": status,
        "label": label,
        "score": round(global_score, 2),
        "quality_score": round(quality_score, 2),
        "risk_score": round(risk_score, 2),
        "signals": all_evidence,
        "reasons": all_reasons,
        "site_type": site_type,
    }


def interpret_score(score: float):
    if score < 0.25:
        return "green", "bajo"
    elif score < 0.55:
        return "yellow", "medio"
    else:
        return "red", "alto"