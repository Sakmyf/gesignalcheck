# ======================================================
# SIGNALCHECK ENGINE v14.0 (FIX REAL CALIBRATION)
# ======================================================

import traceback
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

from backend.Analysis.commercial_risk    import analyze_commercial_risk

from backend.source_analyzer    import analyze_source
from backend.context_classifier import classify_context
from backend.weight_engine      import adjust_weights
from backend.context_adjuster   import adjust_signals_by_context
from backend.confidence_score   import compute_confidence
from backend.insight_generator  import generate_insight
from backend.patterns_engine    import detect_patterns
from backend.narrative_profile  import build_narrative_profile


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
    "uncertainty":        0.15
}


def analyze_context(text: str, url: str = "", title: str = ""):
    try:
        if not text:
            return {"score": 0, "level": "green", "message": "Sin contenido para analizar"}

        context = classify_context(text, url)
        source_info = analyze_source(url)
        weights = adjust_weights(BASE_WEIGHTS, context, source_info)

        # ===============================
        # 🔥 NORMALIZADOR CORRECTO
        # ===============================
        def _get_p(res):
            if isinstance(res, dict):
                val = res.get("score", 0.0)
            else:
                val = getattr(res, "points", 0.0)

            # 🔥 CLAVE: NO usamos abs()
            # solo valores positivos representan riesgo
            return max(0.0, min(val, 1.0))

        # ===============================
        # MÓDULOS
        # ===============================
        credibility    = analyze_credibility(text)
        contradictions = analyze_contradictions(text)
        authority      = analyze_authority(text)
        urgency        = check_urgency(text)
        emotions       = check_emotions(text)
        polarization   = check_polarization(text)
        misinformation = check_misinformation(text)
        scientific     = check_scientific_claims(text)
        narrative      = analyze_narrative_patterns(text)
        hypothetical   = check_hypothetical(text)
        promises       = check_promises(text)
        uncertainty    = detect_uncertainty(text, title, context)

        comm_data = analyze_commercial_risk(text, url)
        comm_normalized = min(0.25, (comm_data.get("score", 0) / 10) * 0.5)

        scores = {
            "credibility":        _get_p(credibility),
            "contradictions":     _get_p(contradictions),
            "authority":          _get_p(authority),
            "urgency":            _get_p(urgency),
            "emotions":           _get_p(emotions),
            "polarization":       _get_p(polarization),
            "misinformation":     _get_p(misinformation),
            "scientific_claims":  _get_p(scientific),
            "narrative_patterns": _get_p(narrative),
            "hypothetical":       _get_p(hypothetical),
            "promises":           _get_p(promises),
            "uncertainty":        _get_p(uncertainty)
        }

        # ===============================
        # SCORE BASE
        # ===============================
        risk_score = sum(scores[k] * weights.get(k, 0.1) for k in scores)
        risk_score += comm_normalized

        trust_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else getattr(authority, "trust_bonus", 0.0)
        url_lower = url.lower() if url else ""

        gov_suffixes = [".gob", ".gov"]
        is_gov = any(s in url_lower for s in gov_suffixes)

        if is_gov:
            risk_score -= (trust_bonus * 3.0) + 0.15
        elif context == "institutional":
            risk_score -= (trust_bonus * 1.5)
        else:
            risk_score -= (trust_bonus * 0.5)

        # ===============================
        # 🔥 CLAMP REAL (SIN piso artificial)
        # ===============================
        risk_score = max(0.0, min(risk_score, 1.0))

        # ===============================
        # 🔥 ESCALA MEJORADA
        # ===============================
        if risk_score < 0.2:
            final_score = int(risk_score * 100)
        elif risk_score < 0.5:
            final_score = int(risk_score * 110)
        else:
            final_score = int(risk_score * 120)

        final_score = min(final_score, 100)

        # ===============================
        # LEVEL
        # ===============================
        if risk_score >= 0.55:
            level = "red"
            message = "Presión narrativa significativa detectada"
        elif risk_score >= 0.20:
            level = "yellow"
            message = "Señales mixtas — lectura crítica recomendada"
        else:
            level = "green"
            message = "Bajo riesgo estructural detectado"

        # ===============================
        # OUTPUT
        # ===============================
        return {
            "score": final_score,
            "level": level,
            "message": message,
            "signals": [],
            "confidence": round(compute_confidence(scores), 2),
            "context": context,
            "source_type": source_info.get("type", "unknown"),
            "commercial_risk": comm_data,
            "pro": {}
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "score": 0,
            "level": "yellow",
            "message": "Error en el motor",
            "signals": [str(e)],
            "confidence": 0
        }