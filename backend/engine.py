# ======================================================
# SIGNALCHECK ENGINE v13.6 — ESTABILIZACIÓN DE ESCALAS
# FIX: Falsos positivos en sitios oficiales (Score 19)
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

# Capa comercial
from backend.Analysis.commercial_risk    import analyze_commercial_risk

from backend.source_analyzer    import analyze_source
from backend.context_classifier import classify_context
from backend.weight_engine      import adjust_weights
from backend.context_adjuster   import adjust_signals_by_context
from backend.confidence_score   import compute_confidence
from backend.insight_generator  import generate_insight
from backend.patterns_engine    import detect_patterns
from backend.narrative_profile  import build_narrative_profile

# Configuración de Pesos Base (v13.6)
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
    if not text:
        return {"score": 0, "level": "green", "message": "Sin contenido para analizar"}

    # 1. Clasificación y Análisis de Fuente
    context = classify_context(text, url)
    source_info = analyze_source(url)
    
    # Ajuste dinámico de pesos según contexto y trust de fuente
    weights = adjust_weights(BASE_WEIGHTS, context, source_info)

    # 2. Ejecución de Módulos Core
    # NOTA: Se asegura que cada módulo entregue puntos normalizados (0-1)
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

    # 3. Módulo Comercial (FIX: Normalización 10 -> 1)
    comm_data = analyze_commercial_risk(text, url)
    # Escala original 0-10 se reduce a 0-1 con tope de influencia en 0.25
    comm_normalized = min(0.25, (comm_data.get("score", 0) / 10) * 0.5)

    # 4. Agregación de Scores con Pesos
    def _get_p(res): return getattr(res, "points", res.get("score", 0.0))

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

    # Suma ponderada inicial
    risk_score = sum(scores[k] * weights.get(k, 0.1) for k in scores)
    
    # Sumamos el riesgo comercial ya normalizado
    risk_score += comm_normalized

    # 5. Ajustes Especiales y Bonos
    # Bono por Autoridad (FIX: Más fuerte para sitios institucionales)
    trust_bonus = authority.get("trust_bonus", 0.0)
    if context == "institutional":
        risk_score -= (trust_bonus * 1.5) # Bono reforzado
    else:
        risk_score -= (trust_bonus * 0.5)

    # 6. Normalización Final y Clasificación
    risk_score = max(0.0, min(risk_score, 1.0))

    if risk_score >= 0.55:
        level, message = "red", "Presión narrativa significativa detectada"
    elif risk_score >= 0.20:
        level, message = "yellow", "Señales mixtas — lectura crítica recomendada"
    else:
        level, message = "green", "Bajo riesgo estructural detectado"

    # 7. Consolidación de Señales (Evidencia)
    def _signals(res): return res.reasons if hasattr(res, "reasons") else res.get("signals", [])

    all_signals = list(dict.fromkeys(
        _signals(credibility)    + _signals(contradictions) +
        _signals(authority)      + _signals(urgency)        +
        _signals(emotions)       + _signals(polarization)   +
        _signals(misinformation) + _signals(scientific)     +
        _signals(narrative)      + _signals(hypothetical)   +
        _signals(promises)       + _signals(uncertainty)    +
        source_info.get("signals", []) + comm_data.get("signals", [])
    ))

    # Limpiar y priorizar señales por contexto
    adjusted_signals = adjust_signals_by_context(all_signals, context)

    # 8. Generación de Metadatos PRO
    confidence = compute_confidence(scores)
    patterns   = detect_patterns(adjusted_signals, risk_score)
    profile    = build_narrative_profile(adjusted_signals, risk_score)
    insight    = generate_insight(patterns, profile)

    return {
        "score":       round(risk_score, 2),
        "level":       level,
        "message":     message,
        "signals":     adjusted_signals[:6],
        "confidence":  round(confidence, 2),
        "insight":     insight,
        "context":     context,
        "source_type": source_info.get("type", "unknown"),
        "commercial_risk": comm_data,
        "pro": {
            "patterns": patterns,
            "narrative_profile": profile,
            "context_note": f"Análisis en modo {context}",
            "_scores": scores
        }
    }