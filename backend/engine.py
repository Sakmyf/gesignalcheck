# ======================================================
# SIGNALCHECK ENGINE v9.0 — FINAL CALIBRATED
# ======================================================

print("🔥 ENGINE v9.0 FINAL CALIBRATED OK")

# ======================================================
# IMPORTS
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

from backend.Analysis.evidence import analyze_evidence
from backend.Analysis.authority import analyze_authority
from backend.Analysis.framing import analyze_framing
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.headline_gap import analyze_headline_gap

from backend.Analysis.patterns_engine import detect_patterns
from backend.Analysis.narrative_profile import build_narrative_profile

from backend.context_classifier import classify_context
from backend.context_adjuster import adjust_signals_by_context
from backend.source_analyzer import analyze_source
from backend.source_adjuster import adjust_score_by_source
from backend.confidence_score import compute_confidence

from backend.utils.analysis_adapter import adapt_dict_to_result
from backend.text_normalizer import normalize_text


MAX_RISK_SCORE = 8.0


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

    # ======================================================
    # MÓDULOS
    # ======================================================

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
    ]

    narrative = adapt_dict_to_result(patterns.analyze(text))
    modules.append(narrative)

    evidence = adapt_dict_to_result(analyze_evidence(text))
    authority = adapt_dict_to_result(analyze_authority(text))
    framing = adapt_dict_to_result(analyze_framing(text))
    contradictions = adapt_dict_to_result(analyze_contradictions(text))
    headline_gap = adapt_dict_to_result(analyze_headline_gap(headline, body or text))

    modules.extend([evidence, authority, framing, contradictions, headline_gap])

    # ======================================================
    # SCORE BASE
    # ======================================================

    total_points = sum(m.points for m in modules)

    risk_score = total_points / MAX_RISK_SCORE

    # ======================================================
    # 🔥 COMPENSACIONES (CLAVE)
    # ======================================================

    # evidencia fuerte baja riesgo
    risk_score -= evidence.points * 0.9

    # autoridad fuerte reduce riesgo
    if authority.points < 0:
        risk_score += authority.points * 0.4

    # fuente confiable reduce riesgo
    if source_info.get("trust_level", 0.5) > 0.8:
        risk_score *= 0.8

    # ======================================================
    # BOOSTS CONTROLADOS
    # ======================================================

    if contradictions.points > 0.5:
        risk_score += 0.12

    if headline_gap.points > 0.5:
        risk_score += 0.10

    if framing.points > 0.6:
        risk_score += 0.08

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # SIGNALS
    # ======================================================

    all_reasons = list(dict.fromkeys(
        r for m in modules for r in m.reasons
    ))

    all_signals = list(dict.fromkeys(
        s for m in modules for s in m.evidence
    ))

    all_signals = adjust_signals_by_context(all_signals, context)

    # ======================================================
    # PATTERNS + PROFILE
    # ======================================================

    patterns_detected = detect_patterns(all_signals, risk_score)
    narrative_profile = build_narrative_profile(all_signals, risk_score)

    # ajuste final por fuente
    risk_score = adjust_score_by_source(risk_score, source_info)

    # ======================================================
    # 🟢 BOOST GLOBAL FINAL (CLAVE)
    # ======================================================

    if evidence.points > 0.5 and source_info.get("trust_level", 0.5) > 0.7:
        risk_score *= 0.7

    # ======================================================
    # INSIGHT
    # ======================================================

    if risk_score < 0.35:
        insight = "contenido confiable"
    elif risk_score < 0.65:
        insight = "requiere lectura crítica"
    else:
        insight = "contenido con presión narrativa"

    confidence = compute_confidence(all_signals, patterns_detected)

    # ======================================================
    # LEVEL
    # ======================================================

    if risk_score < 0.35:
        level = "low"
    elif risk_score < 0.65:
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
# COMPAT
# ======================================================

def analyze_context(text: str, headline: str = "", body: str = "", url: str = ""):
    return analyze_content(text, headline, body, url)