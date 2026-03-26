# ======================================================
# SIGNALCHECK ENGINE v15 — COUNTRY-NEUTRAL + BALANCED
# ======================================================

from backend.Analysis.credibility        import analyze          as analyze_credibility
from backend.Analysis.contradictions     import analyze_contradictions
from backend.Analysis.authority          import analyze_authority
from backend.Analysis.urgency            import check_urgency
from backend.Analysis.emotions           import analyze as check_emotions
from backend.Analysis.polarization       import check_polarization
from backend.Analysis.misinformation     import check_misinformation
from backend.Analysis.scientific_claims  import check_scientific_claims
from backend.Analysis.narrative_patterns import analyze          as analyze_narrative_patterns
from backend.Analysis.hypothetical       import check_hypothetical
from backend.Analysis.promises           import check_promises

from backend.source_analyzer             import analyze_source
from backend.context_classifier         import classify_context
from backend.Analysis.weight_engine     import adjust_weights
from backend.context_adjuster           import adjust_signals_by_context
from backend.confidence_score           import compute_confidence
from backend.insight_generator          import generate_insight
from backend.narrative_profile          import build_narrative_profile
from backend.patterns_engine            import detect_patterns
from backend.structural_score           import calculate_structural_score


BASE_WEIGHTS = {
    "credibility":        0.15,
    "contradictions":     0.10,
    "authority":          0.10,
    "urgency":            0.10,
    "emotions":           0.12,
    "polarization":       0.12,
    "misinformation":     0.10,
    "scientific_claims":  0.08,
    "narrative_patterns": 0.08,
    "hypothetical":       0.05,
    "promises":           0.10,
}


def _score(x):
    if isinstance(x, dict):
        return float(x.get("score", 0.0))
    return float(getattr(x, "points", 0.0))


def _signals(x):
    if isinstance(x, dict):
        return x.get("signals", x.get("reasons", []))
    return list(getattr(x, "reasons", []))


def analyze_context(text: str, url: str = "") -> dict:

    if not text or len(text.strip()) < 30:
        return {
            "score": 0,
            "level": "green",
            "message": "Sin contenido suficiente",
            "signals": [],
            "confidence": 0,
            "structural_index": 0,
            "insight": "",
            "context": "general",
            "pro": {}
        }

    # ==================================================
    # CONTEXTO
    # ==================================================
    context = classify_context(text, url)

    # ==================================================
    # ECOMMERCE → IGNORAR
    # ==================================================
    if context == "ecommerce":
        return {
            "score": 80,
            "level": "green",
            "message": "Contenido comercial",
            "signals": [],
            "confidence": 90,
            "structural_index": 0,
            "insight": "No aplica análisis narrativo.",
            "context": context,
            "pro": {}
        }

    # ==================================================
    # FUENTE (peso reducido)
    # ==================================================
    source_info = analyze_source(url)
    trust       = source_info.get("trust_level", 0.55)

    weights = adjust_weights(BASE_WEIGHTS.copy(), context, source_info)

    # ==================================================
    # MÓDULOS
    # ==================================================
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

    authority_risk  = authority.get("score", 0.0) if isinstance(authority, dict) else 0.0
    authority_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else 0.0

    # ==================================================
    # RISK BASE
    # ==================================================
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
        _score(promises)           * weights["promises"]
    )

    risk_score -= authority_bonus * weights["authority"]

    # ==================================================
    # AJUSTE CONTEXTO (SUAVE)
    # ==================================================
    if context == "institutional":
        risk_score *= 0.75
    elif context == "fact_check":
        risk_score *= 0.70
    elif context == "social":
        risk_score *= 1.15
    elif context == "news_media":
        risk_score *= 0.90

    # ==================================================
    # AJUSTE FUENTE (SUAVE)
    # ==================================================
    if trust >= 0.90:
        risk_score *= 0.75
    elif trust >= 0.80:
        risk_score *= 0.85
    elif trust >= 0.70:
        risk_score *= 0.92
    elif trust <= 0.30:
        risk_score *= 1.15

    # ==================================================
    # POSITIVE SIGNALS
    # ==================================================
    positive = 0.0

    if _score(emotions) < 0.2:
        positive += 0.05

    if _score(urgency) == 0:
        positive += 0.05

    if _score(contradictions) == 0:
        positive += 0.05

    risk_score = max(0.0, min(risk_score - positive, 1.0))

    # ==================================================
    # SCORE FINAL
    # ==================================================
    final_score = (1 - risk_score) * 100

    if final_score > 70:
        level = "green"
    elif final_score > 40:
        level = "yellow"
    else:
        level = "red"

    # ==================================================
    # OUTPUT
    # ==================================================
    module_results = {
        "credibility": _score(credibility),
        "contradictions": _score(contradictions),
        "authority": authority_risk,
        "urgency": _score(urgency),
        "emotions": _score(emotions),
        "polarization": _score(polarization),
        "misinformation": _score(misinformation),
        "scientific_claims": _score(scientific_claims),
        "narrative_patterns": _score(narrative_patterns),
        "hypothetical": _score(hypothetical),
        "promises": _score(promises),
    }

    confidence = compute_confidence(module_results)

    return {
        "score": round(final_score, 0),
        "level": level,
        "confidence": int(confidence * 100),
        "context": context
    }