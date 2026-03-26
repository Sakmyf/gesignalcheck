# ======================================================
# SIGNALCHECK ENGINE v12.1
# + detect_uncertainty (incertidumbre estructural)
# + source_analyzer v3 (clasificación por tipo de fuente)
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

from backend.source_analyzer    import analyze_source
from backend.context_classifier import classify_context
from backend.weight_engine      import adjust_weights
from backend.context_adjuster   import adjust_signals_by_context
from backend.confidence_score   import compute_confidence
from backend.insight_generator  import generate_insight
from backend.narrative_profile  import build_narrative_profile
from backend.patterns_engine    import detect_patterns


# ======================================================
# PESOS BASE — suman 1.00
# ======================================================

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
    "uncertainty":        0.15,   # nuevo
}


# ======================================================
# HELPERS
# ======================================================

def _score(x) -> float:
    if isinstance(x, dict):
        return float(x.get("score", 0.0))
    return float(getattr(x, "points", 0.0))

def _signals(x) -> list:
    if isinstance(x, dict):
        return x.get("signals", x.get("reasons", []))
    return list(getattr(x, "reasons", []))


# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

def analyze_context(text: str, url: str = "", title: str = "") -> dict:

    if not text or len(text.strip()) < 30:
        return {
            "score":      0.0,
            "level":      "green",
            "message":    "Sin contenido suficiente",
            "signals":    [],
            "confidence": 0.0,
            "insight":    "No hay contenido suficiente para analizar.",
            "context":    "general",
            "pro":        {}
        }

    # ======================================================
    # 1. CONTEXTO + FUENTE
    # ======================================================

    context     = classify_context(text)
    source_info = analyze_source(url, text)   # v3: recibe text para media_detector
    trust       = source_info.get("trust_level", 0.55)

    # ======================================================
    # 2. PESOS DINÁMICOS
    # ======================================================

    weights = adjust_weights(BASE_WEIGHTS.copy(), context, source_info)

    # ======================================================
    # 3. ANÁLISIS MODULAR (12 módulos)
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
    uncertainty        = detect_uncertainty(text, title)

    # ======================================================
    # 4. SCORES PONDERADOS
    # ======================================================

    authority_risk  = authority.get("score", 0.0)       if isinstance(authority, dict) else 0.0
    authority_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else 0.0

    risk_score = (
        _score(credibility)        * weights.get("credibility", 0.10)        +
        _score(contradictions)     * weights.get("contradictions", 0.05)     +
        authority_risk             * weights.get("authority", 0.10)          +
        _score(urgency)            * weights.get("urgency", 0.10)            +
        _score(emotions)           * weights.get("emotions", 0.10)           +
        _score(polarization)       * weights.get("polarization", 0.10)       +
        _score(misinformation)     * weights.get("misinformation", 0.10)     +
        _score(scientific_claims)  * weights.get("scientific_claims", 0.08)  +
        _score(narrative_patterns) * weights.get("narrative_patterns", 0.07) +
        _score(hypothetical)       * weights.get("hypothetical", 0.05)       +
        _score(promises)           * weights.get("promises", 0.10)           +
        _score(uncertainty)        * weights.get("uncertainty", 0.15)
    )

    # Trust bonus de autoridad concreta
    risk_score -= authority_bonus * weights.get("authority", 0.10)

    # ======================================================
    # 5. AJUSTE POR FUENTE
    # ======================================================

    if trust >= 0.90:
        risk_score *= 0.40
    elif trust >= 0.80:
        risk_score *= 0.55
    elif trust >= 0.65:
        risk_score *= 0.75
    elif trust >= 0.55:
        risk_score *= 0.90
    elif trust <= 0.30:
        risk_score *= 1.30

    # ======================================================
    # 6. SEÑALES + DEDUPLICACIÓN
    # ======================================================

    all_signals = list(dict.fromkeys(
        _signals(credibility)        +
        _signals(contradictions)     +
        _signals(authority)          +
        _signals(urgency)            +
        _signals(emotions)           +
        _signals(polarization)       +
        _signals(misinformation)     +
        _signals(scientific_claims)  +
        _signals(narrative_patterns) +
        _signals(hypothetical)       +
        _signals(promises)           +
        _signals(uncertainty)        +
        source_info.get("signals", [])
    ))

    adjusted_signals = adjust_signals_by_context(all_signals, context)

    # ======================================================
    # 7. NORMALIZACIÓN
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # 8. CLASIFICACIÓN
    # ======================================================

    if risk_score < 0.25:
        level   = "green"
        message = source_info.get("message", "Bajo riesgo estructural")
    elif risk_score < 0.55:
        level   = "yellow"
        message = "Señales mixtas — lectura crítica recomendada"
    else:
        level   = "red"
        message = "Presión narrativa significativa detectada"

    # ======================================================
    # 9. CAPA PRO
    # ======================================================

    confidence = compute_confidence(adjusted_signals, adjusted_signals)
    patterns   = detect_patterns(adjusted_signals, risk_score)
    profile    = build_narrative_profile(adjusted_signals, risk_score)
    insight    = generate_insight(patterns, profile)

    # ======================================================
    # 10. OUTPUT
    # ======================================================

    return {
        "score":      round(risk_score, 2),
        "level":      level,
        "message":    message,
        "signals":    adjusted_signals[:6],
        "confidence": round(confidence, 2),
        "insight":    insight,
        "context":    context,
        "source_type": source_info.get("type", "unknown"),
        "pro": {
            "patterns":          patterns,
            "narrative_profile": profile,
            "source":            source_info,
            "context":           context,
            "weights_used":      {k: round(v, 3) for k, v in weights.items()},
            "_scores": {
                "credibility":        round(_score(credibility), 3),
                "contradictions":     round(_score(contradictions), 3),
                "authority_risk":     round(authority_risk, 3),
                "authority_bonus":    round(authority_bonus, 3),
                "urgency":            round(_score(urgency), 3),
                "emotions":           round(_score(emotions), 3),
                "polarization":       round(_score(polarization), 3),
                "misinformation":     round(_score(misinformation), 3),
                "scientific_claims":  round(_score(scientific_claims), 3),
                "narrative_patterns": round(_score(narrative_patterns), 3),
                "hypothetical":       round(_score(hypothetical), 3),
                "promises":           round(_score(promises), 3),
                "uncertainty":        round(_score(uncertainty), 3),
                "source_trust":       round(trust, 3),
            }
        }
    }