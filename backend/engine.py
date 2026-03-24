# ======================================================
# SIGNALCHECK ENGINE v10 – PRO BALANCED + CONFIDENCE
# ======================================================

from backend.Analysis.credibility import analyze as analyze_credibility
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.authority import analyze_authority
from backend.Analysis.urgency import check_urgency

from backend.source_analyzer import analyze_source


def analyze_context(text: str, url: str = ""):

    if not text or len(text.strip()) < 30:
        return {
            "score": 0.0,
            "confidence": 0.0,
            "level": "green",
            "message": "Contenido insuficiente",
            "signals": []
        }

    # ======================================================
    # ANALISIS BASE
    # ======================================================

    credibility = analyze_credibility(text)
    contradictions = analyze_contradictions(text)
    authority = analyze_authority(text)
    urgency = check_urgency(text)

    source_info = analyze_source(url)

    # ======================================================
    # HELPERS
    # ======================================================

    def get_score(x):
        if isinstance(x, dict):
            return x.get("score", 0.0)
        return getattr(x, "points", 0.0)

    def get_signals(x):
        if isinstance(x, dict):
            return x.get("signals", [])
        return getattr(x, "reasons", [])

    # ======================================================
    # SCORES BASE
    # ======================================================

    credibility_score = get_score(credibility)
    contradiction_score = get_score(contradictions)
    authority_score = get_score(authority)
    urgency_score = get_score(urgency)

    trust = source_info.get("trust_level", 0.5)

    # ======================================================
    # RISK SCORE (equilibrado real)
    # ======================================================

    risk_score = (
        credibility_score * 0.30 +
        contradiction_score * 0.25 +
        authority_score * 0.20 +
        urgency_score * 0.15 +
        (1 - trust) * 0.10
    )

    # ======================================================
    # AJUSTES INTELIGENTES (clave UX)
    # ======================================================

    # si hay señales múltiples → sube riesgo
    signal_count = (
        len(get_signals(credibility)) +
        len(get_signals(contradictions)) +
        len(get_signals(authority)) +
        len(get_signals(urgency))
    )

    if signal_count >= 3:
        risk_score += 0.1

    # contenido demasiado emocional
    if urgency_score > 0.4 and credibility_score > 0.3:
        risk_score += 0.1

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CONFIDENCE SCORE (nuevo PRO)
    # ======================================================

    confidence_score = (
        trust * 0.5 +
        (1 - authority_score) * 0.2 +
        (1 - contradiction_score) * 0.2 +
        (1 - urgency_score) * 0.1
    )

    confidence_score = max(0.0, min(confidence_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN UX REAL
    # ======================================================

    if risk_score < 0.3:
        level = "green"
        message = "Bajo riesgo estructural"

    elif risk_score < 0.6:
        level = "yellow"
        message = "Contenido con señales mixtas"

    else:
        level = "red"
        message = "Requiere atención"

    # ======================================================
    # SEÑALES
    # ======================================================

    signals = list(set(
        get_signals(credibility) +
        get_signals(contradictions) +
        get_signals(authority) +
        get_signals(urgency) +
        source_info.get("signals", [])
    ))[:6]

    # ======================================================
    # OUTPUT PRO
    # ======================================================

    return {
        "score": round(risk_score, 2),
        "confidence": round(confidence_score, 2),
        "level": level,
        "message": message,
        "signals": signals,
        "source": source_info
    }