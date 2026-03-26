# ======================================================
# SIGNALCHECK ENGINE v13 — BALANCED + COUNTRY-NEUTRAL
# ======================================================

from backend.Analysis.credibility        import analyze          as analyze_credibility
from backend.Analysis.contradictions     import analyze_contradictions
from backend.Analysis.authority          import analyze_authority
from backend.Analysis.urgency            import check_urgency
from backend.Analysis.emotions           import analyze          as check_emotions
from backend.Analysis.polarization       import check_polarization
from backend.Analysis.misinformation     import check_misinformation
from backend.Analysis.scientific_claims  import check_scientific_claims
from backend.Analysis.narrative_patterns import analyze          as analyze_narrative_patterns
from backend.Analysis.hypothetical       import check_hypothetical
from backend.Analysis.promises           import check_promises
from backend.Analysis.detect_uncertainty import detect_uncertainty

from backend.source_analyzer     import analyze_source
from backend.context_classifier import classify_context
from backend.weight_engine      import adjust_weights
from backend.context_adjuster   import adjust_signals_by_context
from backend.confidence_score   import compute_confidence
from backend.insight_generator  import generate_insight
from backend.narrative_profile  import build_narrative_profile
from backend.patterns_engine    import detect_patterns


BASE_WEIGHTS = {
    "credibility":        0.10,
    "contradictions":     0.05,
    "authority":          0.10,
    "urgency":            0.10,
    "emotions":           0.10,
    "polarization":       0.10,
    "misinformation":     0.10,
    "scientific_claims":  0.08,
    "narrative_patterns": 0.07,
    "hypothetical":       0.05,
    "promises":           0.10,
    "uncertainty":        0.15,
}


# ======================================================
# HELPERS
# ======================================================

def _score(x):
    if isinstance(x, dict):
        return float(x.get("score", 0.0))
    return float(getattr(x, "points", 0.0))

def _signals(x):
    if isinstance(x, dict):
        return x.get("signals", x.get("reasons", []))
    return list(getattr(x, "reasons", []))


# ======================================================
# MAIN FUNCTION
# ======================================================

def analyze_context(text: str, url: str = "", title: str = "") -> dict:

    if not text or len(text.strip()) < 30:
        return {
            "score": 0.0,
            "level": "green",
            "message": "Sin contenido suficiente",
            "signals": [],
            "confidence": 0.0,
            "insight": "",
            "context": "general",
            "pro": {}
        }

    # ======================================================
    # CONTEXTO + FUENTE
    # ======================================================

    context     = classify_context(text)
    source_info = analyze_source(url, text)
    trust       = source_info.get("trust_level", 0.55)

    weights = adjust_weights(BASE_WEIGHTS.copy(), context, source_info)

    # ======================================================
    # MÓDULOS
    # ======================================================

    credibility        = analyze_credibility(text)
    contradictions     = analyze_contradictions(text)
    authority          = analyze_authority(text)
    urgency            = check_urgency(text)
    emotions           = check_emotions(text)
    polarization       = check_polarization(text)
    misinformation     = check_misinformation(text)
    scientific_claims  = check_scientific_claims(text)
    narrative_patterns = analyze_narrative_patterns(text)
    hypothetical       = check_hypothetical(text)
    promises           = check_promises(text)

    # 🔥 FIX CLAVE
    uncertainty        = detect_uncertainty(text, title, context)

    authority_risk  = authority.get("score", 0.0)       if isinstance(authority, dict) else 0.0
    authority_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else 0.0

    # ======================================================
    # RISK SCORE BASE
    # ======================================================

    risk_score = (
        _score(credibility)        * weights["credibility"] +
        _score(contradictions)     * weights["contradictions"] +
        authority_risk             * weights["authority"] +
        _score(urgency)            * weights["urgency"] +
        _score(emotions)           * weights["emotions"] +
        _score(polarization)       * weights["polarization"] +
        _score(misinformation)     * weights["misinformation"] +
        _score(scientific_claims)  * weights["scientific_claims"] +
        _score(narrative_patterns) * weights["narrative_patterns"] +
        _score(hypothetical)       * weights["hypothetical"] +
        _score(promises)           * weights["promises"] +
        _score(uncertainty)        * weights["uncertainty"]
    )

    # bonus autoridad
    risk_score -= authority_bonus * weights["authority"]

    # ======================================================
    # AJUSTE POR FUENTE (SUAVIZADO)
    # ======================================================

    if trust >= 0.90:
        risk_score *= 0.75
    elif trust >= 0.80:
        risk_score *= 0.85
    elif trust >= 0.65:
        risk_score *= 0.92
    elif trust >= 0.55:
        risk_score *= 0.98
    elif trust <= 0.30:
        risk_score *= 1.15

    # ======================================================
    # 🔥 SEÑALES POSITIVAS (SUTILEZA)
    # ======================================================

    positive = 0.0

    if _score(emotions) < 0.2:
        positive += 0.03

    if _score(urgency) == 0:
        positive += 0.03

    if _score(contradictions) == 0:
        positive += 0.04

    risk_score = max(0.0, risk_score - positive)

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN (AJUSTADA)
    # ======================================================

    if risk_score < 0.30:
        level = "green"
        message = "Bajo riesgo estructural"
    elif risk_score < 0.60:
        level = "yellow"
        message = "Señales mixtas — lectura crítica recomendada"
    else:
        level = "red"
        message = "Presión narrativa significativa detectada"

    # ======================================================
    # SEÑALES
    # ======================================================

    all_signals = list(dict.fromkeys(
        _signals(credibility) +
        _signals(contradictions) +
        _signals(authority) +
        _signals(urgency) +
        _signals(emotions) +
        _signals(polarization) +
        _signals(misinformation) +
        _signals(scientific_claims) +
        _signals(narrative_patterns) +
        _signals(hypothetical) +
        _signals(promises) +
        _signals(uncertainty) +
        source_info.get("signals", [])
    ))

    adjusted_signals = adjust_signals_by_context(all_signals, context)

    # ======================================================
    # PRO LAYER
    # ======================================================

    confidence = compute_confidence(adjusted_signals, adjusted_signals)
    patterns   = detect_patterns(adjusted_signals, risk_score)
    profile    = build_narrative_profile(adjusted_signals, risk_score)
    insight    = generate_insight(patterns, profile)

    # ======================================================
    # OUTPUT
    # ======================================================

    return {
        "score": round(risk_score, 2),
        "level": level,
        "message": message,
        "signals": adjusted_signals[:6],
        "confidence": round(confidence, 2),
        "insight": insight,
        "context": context,
        "source_type": source_info.get("type", "unknown"),
        "pro": {
            "patterns": patterns,
            "narrative_profile": profile,
            "source": source_info,
        }
    }