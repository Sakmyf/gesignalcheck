# ======================================================
# SIGNALCHECK ENGINE v9.6 – BALANCED + STABLE
# ======================================================

from backend.Analysis.credibility import analyze as analyze_credibility
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.authority import analyze_authority
from backend.Analysis.urgency import check_urgency

from backend.source_analyzer import analyze_source


def analyze_context(text: str, url: str = ""):

    if not text:
        return {
            "score":   0.0,
            "level":   "green",
            "signals": [],
            "message": "Sin contenido",
            "_scores": {}
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
        # 🔥 clave: evitamos negativos y overflow
        return max(0.0, min(abs(score), 1.0))

    # ======================================================
    # SCORES NORMALIZADOS
    # ======================================================

    narrative_score   = normalize(get_score(credibility))
    rhetorical_score  = normalize(get_score(contradictions))
    urgency_score     = normalize(get_score(urgency))

    # FIX P0: authority tiene dos efectos separados.
    # authority_risk  → autoridad débil suma riesgo
    # authority_bonus → autoridad fuerte resta riesgo
    authority_risk  = normalize(authority.get("score",       0.0) if isinstance(authority, dict) else getattr(authority, "points", 0.0))
    authority_bonus = normalize(authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else 0.0)

    # ======================================================
    # SCORE BASE
    # ======================================================

    risk_score = (
        narrative_score  * 0.25 +
        rhetorical_score * 0.25 +
        urgency_score    * 0.10 +
        authority_risk   * 0.15   # autoridad vaga contribuye al riesgo
    )

    # autoridad concreta reduce riesgo
    risk_score -= authority_bonus * 0.20

    # baseline mínimo (evita todo en 0)
    risk_score += 0.05

    # ======================================================
    # ANALISIS DE FUENTE
    # ======================================================

    source_info = analyze_source(url)
    trust = source_info.get("trust_level", 0.5)

    # ajuste progresivo (suave, no agresivo)
    if trust >= 0.85:
        risk_score *= 0.5

    elif trust >= 0.7:
        risk_score *= 0.7

    elif trust <= 0.3:
        risk_score *= 1.25

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN (UX CALIBRADA)
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
        "score":   round(risk_score, 2),
        "level":   level,
        "message": message,
        "signals": signals,
        "source":  source_info,
        # Scores individuales — uso interno (DB/analytics).
        # No se exponen en el response al cliente.
        "_scores": {
            "narrative":       round(narrative_score,  2),
            "rhetorical":      round(rhetorical_score, 2),
            "urgency":         round(urgency_score,    2),
            "authority_risk":  round(authority_risk,   2),
            "authority_bonus": round(authority_bonus,  2),
            "source_trust":    round(trust,            2),
        }
    }