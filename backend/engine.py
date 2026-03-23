# ======================================================
# SIGNALCHECK ENGINE v9.3 – STABLE CALIBRATED
# ======================================================

from backend.Analysis.credibility import analyze as analyze_credibility
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.authority import analyze_authority
from backend.Analysis.urgency import check_urgency

from backend.source_analyzer import analyze_source
from backend.source_adjuster import adjust_score_by_source


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
    # NORMALIZACIÓN DE SALIDAS
    # (COMPATIBLE dict / objeto)
    # ======================================================

    def get_score(x):
        if isinstance(x, dict):
            return x.get("score", 0.0)
        return getattr(x, "points", 0.0)

    def get_signals(x):
        if isinstance(x, dict):
            return x.get("signals", [])
        return getattr(x, "reasons", [])

    # EXTRAER SCORES (FIX CRÍTICO)
    narrative_score = get_score(credibility)
    rhetorical_score = get_score(contradictions)
    absence_score = 0.2 if narrative_score > 0.5 else 0.0  # proxy suave
    authority_score = get_score(authority)
    urgency_score = get_score(urgency)

    # ======================================================
    # SCORE BASE (BALANCEADO)
    # ======================================================

    risk_score = (
        narrative_score * 0.25 +
        rhetorical_score * 0.25 +
        absence_score * 0.15 +
        authority_score * 0.2 +
        urgency_score * 0.15
    )

    # ======================================================
    # ANALISIS DE FUENTE (CLAVE)
    # ======================================================

    source_info = analyze_source(url)
    trust = source_info.get("trust_level", 0.5)

    # ajuste fuerte (esto arregla el "todo rojo")
    if trust >= 0.8:
        risk_score *= 0.6
    elif trust >= 0.6:
        risk_score *= 0.8
    elif trust <= 0.3:
        risk_score *= 1.2

    # también aplicamos el adjuster si querés mantenerlo
    risk_score = adjust_score_by_source(risk_score, source_info)

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN FINAL (IMPORTANTE)
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

    # limpiar duplicados
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