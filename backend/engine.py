# ======================================================
# SIGNALCHECK ENGINE v13.1 — CONTEXT + HEADLINE INTELLIGENCE
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
# PRIORITIZATION LAYER
# ======================================================

def _detect_content_type(text: str, url: str) -> str:

    text = text.lower()
    url = url.lower()

    if any(w in text for w in ["comprar", "oferta", "envío", "carrito"]):
        return "ecommerce"

    if ".gov" in url or ".edu" in url:
        return "institutional"

    if any(w in text for w in ["según", "informó", "reportó", "fuentes"]):
        return "news"

    return "generic"


def _apply_signal_prioritization(context_type, scores_dict):

    if context_type == "ecommerce":
        scores_dict["urgency"] *= 0.4

    if context_type == "news":
        scores_dict["uncertainty"] *= 0.8   # 🔥 ajustado

    if context_type == "institutional":
        scores_dict["emotions"] *= 0.6

    return scores_dict


def _combo_boost(scores_dict):

    bonus = 0.0

    if scores_dict["urgency"] > 0.5 and scores_dict["emotions"] > 0.5:
        bonus += 0.10

    if scores_dict["promises"] > 0.5 and scores_dict["credibility"] > 0.5:
        bonus += 0.15

    return bonus


def _headline_boost(title: str):

    if not title:
        return 0.0

    title = title.lower()

    boost = 0.0

    # palabras sensacionalistas
    if any(word in title for word in [
        "brutal", "impactante", "terrible", "explosión",
        "horror", "dramático", "escándalo", "urgente"
    ]):
        boost += 0.20

    # signos
    if "!" in title or '"' in title:
        boost += 0.10

    return boost


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

    # DEBUG (para errores tipo MercadoLibre)
    if len(text) < 80:
        print("⚠️ TEXTO CORTO:", url)

    # ======================================================
    # CONTEXTO + FUENTE
    # ======================================================

    context     = classify_context(text)
    source_info = analyze_source(url, text)
    trust       = source_info.get("trust_level", 0.55)

    weights = adjust_weights(BASE_WEIGHTS.copy(), context, source_info)

    content_type = _detect_content_type(text, url)

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

    uncertainty        = detect_uncertainty(text, title, context)

    authority_risk  = authority.get("score", 0.0)       if isinstance(authority, dict) else 0.0
    authority_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else 0.0

    # ======================================================
    # SCORES
    # ======================================================

    scores = {
        "credibility":        _score(credibility),
        "contradictions":     _score(contradictions),
        "authority":          authority_risk,
        "urgency":            _score(urgency),
        "emotions":           _score(emotions),
        "polarization":       _score(polarization),
        "misinformation":     _score(misinformation),
        "scientific_claims":  _score(scientific_claims),
        "narrative_patterns": _score(narrative_patterns),
        "hypothetical":       _score(hypothetical),
        "promises":           _score(promises),
        "uncertainty":        _score(uncertainty),
    }

    # ======================================================
    # PRIORITIZATION
    # ======================================================

    scores = _apply_signal_prioritization(content_type, scores)

    # ======================================================
    # RISK SCORE
    # ======================================================

    risk_score = sum(scores[k] * weights[k] for k in scores)

    risk_score += _combo_boost(scores)

    # 🔥 HEADLINE BOOST (CLAVE)
    # fallback si no hay title
    headline_source = title

    if not headline_source or len(headline_source.strip()) < 10:
        headline_source = text[:200]  # primeros caracteres del contenido

    risk_score += _headline_boost(headline_source)

    risk_score -= authority_bonus * weights["authority"]

    # ======================================================
    # AJUSTE POR FUENTE
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
    # SEÑALES POSITIVAS
    # ======================================================

    positive = 0.0

    if scores["emotions"] < 0.2:
        positive += 0.03

    if scores["urgency"] == 0:
        positive += 0.03

    if scores["contradictions"] == 0:
        positive += 0.04

    risk_score = max(0.0, risk_score - positive)

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN
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
    # PRO
    # ======================================================

    confidence = compute_confidence(adjusted_signals, adjusted_signals)
    patterns   = detect_patterns(adjusted_signals, risk_score)
    profile    = build_narrative_profile(adjusted_signals, risk_score)
    insight    = generate_insight(patterns, profile)

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