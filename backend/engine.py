print("ENGINE RULE ENGINE 6.2.1 COGNITIVE PROTECTION ACTIVE")
print("🔥 ENGINE.PY 6.2.1 ACTIVO")

ENGINE_VERSION = "6.2.1"
ENGINE_MODE = "hybrid_narrative_scientific"

from backend.Analysis.emotions import check_emotions
from backend.Analysis.credibility import check_credibility
from backend.Analysis.misinformation import check_misinformation
from backend.Analysis.structural import check_structural
from backend.Analysis.urgency import check_urgency
from backend.Analysis.promises import check_promises
from backend.Analysis.polarization import check_polarization
from backend.Analysis.scientific_claims import check_scientific_claims
from backend.Analysis.hypothetical import check_hypothetical
from urllib.parse import urlparse

# ===============================
# Configuración estratégica
# ===============================

MAX_QUALITY_SCORE = 4.0
MAX_RISK_SCORE = 8.0

EMOTION_WEIGHT = 1.6
POLARIZATION_WEIGHT = 1.7
URGENCY_WEIGHT = 1.4
PROMISE_WEIGHT = 1.4


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

    emotions = check_emotions(text)
    credibility = check_credibility(text)
    misinformation = check_misinformation(text)
    structural = check_structural(text)
    urgency = check_urgency(text)
    promises = check_promises(text)
    polarization = check_polarization(text)
    scientific = check_scientific_claims(text)
    hypothetical = check_hypothetical(text)

    # ===============================
    # QUALITY
    # ===============================

    quality_points = (
        max(credibility.points, 0) +
        max(structural.points, 0)
    )

    # ===============================
    # RISK
    # ===============================

    risk_points = 0.0

    risk_points += abs(min(emotions.points * EMOTION_WEIGHT, 0))
    risk_points += abs(min(polarization.points * POLARIZATION_WEIGHT, 0))
    risk_points += abs(min(urgency.points * URGENCY_WEIGHT, 0))
    risk_points += abs(min(promises.points * PROMISE_WEIGHT, 0))
    risk_points += abs(min(misinformation.points, 0))
    risk_points += abs(min(scientific.points, 0))
    risk_points += abs(min(hypothetical.points, 0))

    # ===============================
    # Bonus manipulación combinada
    # ===============================

    strong_signals = 0

    if emotions.points < -0.7:
        strong_signals += 1
    if polarization.points < -0.6:
        strong_signals += 1
    if urgency.points < -0.5:
        strong_signals += 1

    if strong_signals >= 2:
        risk_points += 1.2

    # ===============================
    # Ajuste por tipo de sitio
    # ===============================

    if site_type == "institutional":
        risk_points *= 0.7
    elif site_type == "media":
        risk_points *= 0.9
    elif site_type == "social":
        risk_points *= 1.15

    # ===============================
    # Normalización
    # ===============================

    quality_score = max(min(quality_points / MAX_QUALITY_SCORE, 1.0), 0.0)
    risk_score = max(min(risk_points / MAX_RISK_SCORE, 1.0), 0.0)

    global_score = (risk_score * 0.75) + ((1 - quality_score) * 0.25)
    global_score = round(global_score, 4)

    # ===============================
    # Decisión visual
    # ===============================

    if global_score < 0.25:
        status = "green"
        label = "contenido informativo"
    elif global_score < 0.55:
        status = "yellow"
        label = "requiere lectura crítica"
    else:
        status = "red"
        label = "presión narrativa significativa"

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
        polarization.reasons +
        scientific.reasons +
        hypothetical.reasons
    )

    all_evidence = (
        emotions.evidence +
        credibility.evidence +
        misinformation.evidence +
        structural.evidence +
        urgency.evidence +
        promises.evidence +
        polarization.evidence +
        scientific.evidence +
        hypothetical.evidence
    )

    return {
        "engine_version": ENGINE_VERSION,
        "engine_mode": ENGINE_MODE,
        "status": status,
        "label": label,
        "score": round(global_score, 2),
        "quality_score": round(quality_score, 2),
        "risk_score": round(risk_score, 2),
        "site_type": site_type,
        "signals": all_evidence,
        "reasons": all_reasons,
    }


def interpret_score(score: float):
    if score < 0.25:
        return "green", "bajo"
    elif score < 0.55:
        return "yellow", "medio"
    else:
        return "red", "alto"