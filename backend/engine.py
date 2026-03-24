# ======================================================
# SIGNALCHECK ENGINE v9.7 – FINAL STABLE + CONTEXT
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
    # NORMALIZACIÓN SEGURA
    # ======================================================

    def get_score(x):
        if isinstance(x, dict):
            return x.get("score", 0.0)
        return getattr(x, "points", 0.0)

    def get_signals(x):
        if isinstance(x, dict):
            return x.get("signals", [])
        return getattr(x, "reasons", [])

    def normalize(score):
        return max(0.0, min(abs(score), 1.0))

    # ======================================================
    # SCORES NORMALIZADOS
    # ======================================================

    narrative_score = normalize(get_score(credibility))
    rhetorical_score = normalize(get_score(contradictions))
    authority_score = normalize(get_score(authority))
    urgency_score = normalize(get_score(urgency))

    # ======================================================
    # SCORE BASE
    # ======================================================
    # authority RESTA riesgo (clave)

    risk_score = (
        narrative_score * 0.25 +
        rhetorical_score * 0.25 +
        urgency_score * 0.1
    )

    # resta por autoridad
    risk_score -= authority_score * 0.2

    # baseline mínimo
    risk_score += 0.05

    # ======================================================
    # ANALISIS DE FUENTE
    # ======================================================

    source_info = analyze_source(url)
    trust = source_info.get("trust_level", 0.5)
    domain = source_info.get("domain", "").lower()
    source_type = source_info.get("type", "")

    # ajuste por confianza
    if trust >= 0.85:
        risk_score *= 0.5

    elif trust >= 0.7:
        risk_score *= 0.7

    elif trust <= 0.3:
        risk_score *= 1.25

    # ======================================================
    # CONTEXT AWARE (CLAVE PRO)
    # ======================================================

    if "facebook" in domain or "twitter" in domain or "instagram" in domain:
        risk_score *= 0.9  # redes más flexibles

    elif ".gov" in domain:
        risk_score *= 1.1  # gobierno más exigente

    elif source_type == "recognized_media":
        risk_score *= 1.05  # medios un poco más exigentes

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN FINAL
    # ======================================================

    if risk_score < 0.30:
        level = "green"
        message = "El contenido no presenta patrones estructurales de riesgo."

    elif risk_score < 0.60:
        level = "yellow"
        message = "El contenido requiere lectura crítica."

    else:
        level = "red"
        message = "Se detectan múltiples señales estructurales de riesgo."

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