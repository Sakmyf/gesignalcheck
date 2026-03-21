print("🔥 ENGINE v8.7 REAL OK")
# ======================================================
# SIGNALCHECK ENGINE v11.0 FINAL + UX READY
# ======================================================

from backend.modules import (
    emotions,
    credibility,
    misinformation,
    structural,
    urgency,
    promises,
    polarization,
    scientific,
    hypothetical,
    patterns
)

# 🔥 NUEVOS MÓDULOS
from backend.analysis.evidence import analyze_evidence
from backend.analysis.authority import analyze_authority
from backend.analysis.framing import analyze_framing
from backend.analysis.contradictions import analyze_contradictions
from backend.analysis.headline_gap import analyze_headline_gap

# 🔥 CAPAS INTELIGENTES
from backend.analysis.patterns_engine import detect_patterns
from backend.analysis.narrative_profile import build_narrative_profile
from backend.analysis.insight_generator import generate_insight
from backend.analysis.context_classifier import classify_context
from backend.analysis.context_adjuster import adjust_signals_by_context
from backend.analysis.source_analyzer import analyze_source
from backend.analysis.source_adjuster import adjust_score_by_source
from backend.analysis.confidence_score import compute_confidence

# 🔥 UTILS
from backend.utils.analysis_adapter import adapt_dict_to_result
from backend.utils.text_normalizer import normalize_text


MAX_RISK_SCORE = 10.0


def analyze_content(text: str, headline: str = "", body: str = "", url: str = ""):
    """
    Motor principal de análisis SignalCheck – versión final lista para producto
    """

    # ======================================================
    # 🛑 FALLBACK
    # ======================================================

    if not text or len(text.strip()) < 30:
        return {
            "risk_score": 0.0,
            "risk_level": "low",
            "confidence": 0.2,
            "insight": "Contenido insuficiente para análisis",
            "context": "unknown",
            "source": {},
            "reasons": [],
            "signals": [],
            "patterns": [],
            "profile": {},
            "total_modules": 0
        }

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    text = normalize_text(text)

    # ======================================================
    # CONTEXTO Y FUENTE
    # ======================================================

    context = classify_context(text)
    source_info = analyze_source(url)

    # ======================================================
    # MÓDULOS BASE
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
        patterns.analyze(text)
    ]

    # ======================================================
    # NUEVOS MÓDULOS
    # ======================================================

    evidence = adapt_dict_to_result(analyze_evidence(text), 1.2, "evidence:")
    authority = adapt_dict_to_result(analyze_authority(text), 0.8, "authority:")
    framing = adapt_dict_to_result(analyze_framing(text), 1.0, "framing:")
    contradictions = adapt_dict_to_result(analyze_contradictions(text), 1.5, "contradiction:")
    headline_gap = adapt_dict_to_result(analyze_headline_gap(headline, body or text), 1.3, "headline:")

    modules.extend([
        evidence,
        authority,
        framing,
        contradictions,
        headline_gap
    ])

    # ======================================================
    # SCORE BASE
    # ======================================================

    total_points = sum(m.points for m in modules)
    risk_score = max(min(abs(total_points) / MAX_RISK_SCORE, 1.0), 0.0)

    # ======================================================
    # REASONS + SIGNALS
    # ======================================================

    all_reasons = list(dict.fromkeys(
        r for m in modules for r in m.reasons
    ))

    all_signals = list(dict.fromkeys(
        s for m in modules for s in m.evidence
    ))

    # ======================================================
    # AJUSTE POR CONTEXTO
    # ======================================================

    all_signals = adjust_signals_by_context(all_signals, context)

    # ======================================================
    # PATTERNS
    # ======================================================

    patterns_detected = detect_patterns(all_signals, risk_score)

    # ======================================================
    # PROFILE
    # ======================================================

    narrative_profile = build_narrative_profile(all_signals, risk_score)

    # ======================================================
    # AJUSTE POR FUENTE
    # ======================================================

    risk_score = adjust_score_by_source(risk_score, source_info)

    # ======================================================
    # INSIGHT (UX CLAVE)
    # ======================================================

    insight = generate_insight(patterns_detected, narrative_profile)

    # ======================================================
    # CONFIDENCE
    # ======================================================

    confidence = compute_confidence(all_signals, patterns_detected)

    # ======================================================
    # NIVEL FINAL
    # ======================================================

    if risk_score < 0.3:
        level = "low"
    elif risk_score < 0.6:
        level = "medium"
    else:
        level = "high"

    # ======================================================
    # OUTPUT FINAL (READY FOR UI)
    # ======================================================

    return {
        "risk_score": round(risk_score, 3),
        "risk_level": level,
        "confidence": round(confidence, 3),
        "insight": insight,
        "context": context,
        "source": source_info,
        "reasons": all_reasons[:5],   # FREE LIMIT
        "signals": all_signals,
        "patterns": patterns_detected,
        "profile": narrative_profile,
        "total_modules": len(modules)
    }