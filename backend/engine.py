# ======================================================
# SIGNALCHECK ENGINE v9.4 – BALANCED REAL USE
# ======================================================

from backend.Analysis.credibility import analyze as analyze_credibility
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.authority import analyze_authority
from backend.Analysis.urgency import check_urgency

from backend.source_analyzer import analyze_source


def analyze_context(text: str, url: str = ""):

    if not text:
        return {
            "score": 0.0,
            "level": "green",
            "signals": [],
            "message": "Sin contenido"
        }

    # ======================================================
    # ANALISIS BASE
    # ======================================================

    credibility = analyze_credibility(text)
    contradictions = analyze_contradictions(text)
    authority = analyze_authority(text)
    urgency = check_urgency(text)

    # ======================================================
    # NORMALIZACIÓN (COMPATIBLE)
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
    # SCORES (FIX CRÍTICO)
    # ======================================================

    narrative_score = get_score(credibility)
    rhetorical_score = get_score(contradictions)
    authority_score = get_score(authority)
    urgency_score = get_score(urgency)

    # ======================================================
    # SCORE BASE (BALANCEADO REAL)
    # ======================================================

    risk_score = (
        narrative_score * 0.2 +
        rhetorical_score * 0.2 +
        authority_score * 0.15 +
        urgency_score * 0.1
    )

    # ======================================================
    # ANALISIS DE FUENTE (CLAVE REAL)
    # ======================================================

    source_info = analyze_source(url)
    trust = source_info.get("trust_level", 0.5)

    # ajuste REAL (esto destraba el "todo rojo")
    if trust >= 0.8:
        risk_score *= 0.5

    elif trust >= 0.6:
        risk_score *= 0.75

    elif trust <= 0.3:
        risk_score *= 1.2

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN REAL (UX IMPORTANTE)
    # ======================================================

    if risk_score < 0.35:
        level = "green"
        message = "Contenido con estructura confiable"

    elif risk_score < 0.65:
        level = "yellow"
        message = "Contenido con señales mixtas"

    else:
        level = "red"
        message = "Requiere atención"

    # ======================================================
    # SEÑALES
    # ======================================================

    signals = (
        get_signals(credibility) +
        get_signals(contradictions) +
        get_signals(authority) +
        get_signals(urgency) +
        source_info.get("signals", [])
    )

    signals = list(set(signals))[:6]

    # ======================================================
    # OUTPUT FINAL
    # ======================================================

    return {
        "score": round(risk_score, 2),
        "level": level,
        "message": message,
        "signals": signals,
        "source": source_info
    }