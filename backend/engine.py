# ======================================================
# SIGNALCHECK ENGINE v8.7 — CLEAN STABLE (NO MODULES)
# ======================================================

print("🔥 ENGINE v8.7 REAL OK")

# ======================================================
# IMPORTS REALES (tu estructura actual)
# ======================================================

from backend.Analysis import (
    emotions,
    credibility,
    misinformation,
    structural,
    urgency,
    promises,
    polarization,
    scientific_claims as scientific,
    hypothetical,
    narrative_patterns as patterns
)

# NUEVOS MÓDULOS
from backend.Analysis.evidence import analyze_evidence
from backend.Analysis.authority import analyze_authority
from backend.Analysis.framing import analyze_framing
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.headline_gap import analyze_headline_gap

# CAPAS
from backend.Analysis.patterns_engine import detect_patterns
from backend.Analysis.narrative_profile import build_narrative_profile
from backend.context_classifier import classify_context
from backend.context_adjuster import adjust_signals_by_context
from backend.source_analyzer import analyze_source
from backend.source_adjuster import adjust_score_by_source
from backend.confidence_score import compute_confidence

# UTILS
from backend.utils.analysis_adapter import adapt_dict_to_result
from backend.text_normalizer import normalize_text


MAX_RISK_SCORE = 10.0


# ======================================================
# CORE
# ======================================================

def analyze_content(text: str, headline: str = "", body: str = "", url: str = ""):

    if not text or len(text.strip()) < 30:
        return {
            "risk_score": 0.0,
            "risk_level": "low",
            "confidence": 0.2,
            "insight": "contenido insuficiente",
            "context": "unknown",
            "source": {},
            "reasons": [],
            "signals": [],
            "patterns": [],
            "profile": {},
            "total_modules": 0
        }

    text = normalize_text(text)

    context = classify_context(text)
    source_info = analyze_source(url)

    modules = [
        emotions.analyze(text),
        credibility.analyze(text),
        misinformation.analyze(text),
        structural.analyze(text),
        urgency.analyze(text),
        promises.analyze(text),
        polarization.analyze(text),
        scientific.analyze(text),
        hypothetical.analyze(text),
        patterns.analyze(text)
    ]

    # NUEVOS
    evidence = adapt_dict_to_result(analyze_evidence(text), 1.8, "evidence:")
    authority = adapt_dict_to_result(analyze_authority(text), 0.8, "authority:")
    framing = adapt_dict_to_result(analyze_framing(text), 1.2, "framing:")
    contradictions = adapt_dict_to_result(analyze_contradictions(text), 2.2, "contradiction:")
    headline_gap = adapt_dict_to_result(analyze_headline_gap(headline, body or text), 1.6, "headline:")

    modules.extend([evidence, authority, framing, contradictions, headline_gap])

    total_points = sum(m.points for m in modules)
    risk_score = max(min(abs(total_points) / MAX_RISK_SCORE, 1.0), 0.0)

    # BOOST
    if contradictions.points > 0.4:
        risk_score += 0.25

    if evidence.points < 0.3:
        risk_score += 0.2

    if headline_gap.points > 0.4:
        risk_score += 0.2

    if framing.points > 0.5:
        risk_score += 0.15

    risk_score = min(risk_score, 1.0)

    # REASONS
    all_reasons = list(dict.fromkeys(
        r for m in modules for r in m.reasons
    ))

    # SIGNALS
    all_signals = list(dict.fromkeys(
        s for m in modules for s in m.evidence
    ))

    # CONTEXTO
    all_signals = adjust_signals_by_context(all_signals, context)

    # PATTERNS
    patterns_detected = detect_patterns(all_signals, risk_score)

    # PROFILE
    narrative_profile = build_narrative_profile(all_signals, risk_score)

    # SOURCE
    risk_score = adjust_score_by_source(risk_score, source_info)

    # INSIGHT
    if risk_score < 0.3:
        insight = "contenido informativo"
    elif risk_score < 0.6:
        insight = "requiere lectura crítica"
    else:
        insight = "contenido con presión narrativa"

    # CONFIDENCE
    confidence = compute_confidence(all_signals, patterns_detected)

    # LEVEL
    if risk_score < 0.3:
        level = "low"
    elif risk_score < 0.6:
        level = "medium"
    else:
        level = "high"

    return {
        "risk_score": round(risk_score, 3),
        "risk_level": level,
        "confidence": round(confidence, 3),
        "insight": insight,
        "context": context,
        "source": source_info,
        "reasons": all_reasons[:5],
        "signals": all_signals,
        "patterns": patterns_detected,
        "profile": narrative_profile,
        "total_modules": len(modules)
    }


# ======================================================
# COMPATIBILIDAD APP.PY
# ======================================================

def analyze_context(text: str, headline: str = "", body: str = "", url: str = ""):
    return analyze_content(text, headline, body, url)