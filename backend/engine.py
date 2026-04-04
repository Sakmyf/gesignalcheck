# ======================================================
# SIGNALCHECK ENGINE v13.8
# FIX: Score 0-100, dimensiones context-aware, dominant_pattern por peso
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
    try:
        if not text:
            return {"score": 0, "level": "green", "message": "Sin contenido para analizar"}

        # 1. Clasificación y Análisis de Fuente
        context = classify_context(text, url)
        source_info = analyze_source(url)
        
        # Ajuste dinámico de pesos según contexto y trust de fuente
        weights = adjust_weights(BASE_WEIGHTS, context, source_info)

        # 2. Ejecución de Módulos Core
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

        # 3. Módulo Comercial 
        comm_data = analyze_commercial_risk(text, url)
        comm_normalized = min(0.25, (comm_data.get("score", 0) / 10) * 0.5)

        # 4. Agregación de Scores con Pesos
        def _get_p(res): 
            if isinstance(res, dict):
                return res.get("score", 0.0)
            return getattr(res, "points", 0.0)

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

        risk_score = sum(scores[k] * weights.get(k, 0.1) for k in scores)
        risk_score += comm_normalized

        # =========================================================
        # 5. AJUSTES ESPECIALES Y BONOS (FIX: SÚPER BONO HISPANO)
        # =========================================================
        trust_bonus = authority.get("trust_bonus", 0.0) if isinstance(authority, dict) else getattr(authority, "trust_bonus", 0.0)
        
        url_lower = url.lower() if url else ""
        
        # Dominios oficiales de LATAM, España y entidades globales puras
        gov_suffixes = [
            ".gob.ar", ".gov.ar", ".gob.cl", ".gov.cl", ".gob.pe", ".gob.mx", 
            ".gob.es", ".gov.co", ".gob.ec", ".gob.bo", ".gob.ve", ".gub.uy", 
            ".gov.py", ".gob.do", ".gob.sv", ".gob.gt", ".gob.hn", ".gob.ni", 
            ".gob.pa", ".go.cr", ".pr.gov"
        ]
        
        is_ibero_gov = any(s in url_lower for s in gov_suffixes)

        if is_ibero_gov:
            # Neutralizador masivo: Borra hasta ~25 puntos de "ruido burocrático"
            risk_score -= (trust_bonus * 3.0) + 0.15 
        elif context == "institutional":
            risk_score -= (trust_bonus * 1.5) 
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

        # 7. Consolidación de Señales
        def _signals(res): 
            if isinstance(res, dict):
                return res.get("signals", [])
            return getattr(res, "reasons", [])

        all_signals = list(dict.fromkeys(
            _signals(credibility)    + _signals(contradictions) +
            _signals(authority)      + _signals(urgency)        +
            _signals(emotions)       + _signals(polarization)   +
            _signals(misinformation) + _signals(scientific)     +
            _signals(narrative)      + _signals(hypothetical)   +
            _signals(promises)       + _signals(uncertainty)    +
            source_info.get("signals", []) + comm_data.get("signals", [])
        ))

        adjusted_signals = adjust_signals_by_context(all_signals, context)

        # 8. Generación de Metadatos PRO
        confidence = compute_confidence(scores)
        patterns   = detect_patterns(adjusted_signals, risk_score)
        profile    = build_narrative_profile(adjusted_signals, risk_score)
        insight    = generate_insight(patterns, profile)

        # =========================================================
        # 9. BLOQUE PRO ESTRUCTURADO — v13.8
        # =========================================================

        def _pct(v): return round(min(max(v, 0.0), 1.0) * 100)

        def _dim_label(pct):
            if pct >= 70: return "Alto"
            if pct >= 40: return "Moderado"
            if pct >= 15: return "Leve"
            return "Sin señales"

        def _get_signals(res):
            if isinstance(res, dict):
                return res.get("signals", [])
            return getattr(res, "reasons", [])

        # — Ajuste emocional por contexto —
        # En noticias la emoción es esperable → la reducimos
        # En ecommerce la emoción es sospechosa → la amplificamos
        def _adjust_emocional(raw, ctx):
            multipliers = {
                "news":          0.6,   # emoción válida en periodismo
                "institutional": 0.4,   # emoción rara → muy sospechosa si aparece
                "ecommerce":     1.4,   # urgencia emocional = presión de compra
                "social":        1.0,   # neutro
                "general":       1.0,
            }
            m = multipliers.get(ctx, 1.0)
            return _pct(raw * m)

        # — Dimensiones (5 ejes del radar) —
        raw_emocional    = (scores["emotions"] + scores["urgency"]) / 2
        dim_emocional    = _adjust_emocional(raw_emocional, context)
        dim_narrativo    = _pct((scores["narrative_patterns"] + scores["hypothetical"]) / 2)
        dim_credibilidad = _pct((scores["credibility"] + scores["contradictions"]) / 2)
        dim_cientifico   = _pct((scores["scientific_claims"] + scores["promises"]) / 2)
        dim_comercial    = _pct(comm_data.get("score", 0) / 10)

        dimensions = {
            "emocional": {
                "score": dim_emocional,
                "label": _dim_label(dim_emocional),
                "signals": list(dict.fromkeys(
                    _get_signals(emotions) + _get_signals(urgency)
                ))[:3]
            },
            "narrativo": {
                "score": dim_narrativo,
                "label": _dim_label(dim_narrativo),
                "signals": list(dict.fromkeys(
                    _get_signals(narrative) + _get_signals(hypothetical)
                ))[:3]
            },
            "credibilidad": {
                "score": dim_credibilidad,
                "label": _dim_label(dim_credibilidad),
                "signals": list(dict.fromkeys(
                    _get_signals(credibility) + _get_signals(contradictions)
                ))[:3]
            },
            "cientifico": {
                "score": dim_cientifico,
                "label": _dim_label(dim_cientifico),
                "signals": list(dict.fromkeys(
                    _get_signals(scientific) + _get_signals(promises)
                ))[:3]
            },
            "comercial": {
                "score": dim_comercial,
                "label": _dim_label(dim_comercial),
                "signals": comm_data.get("signals", [])[:3]
            }
        }

        # — Patrón dominante por impacto real —
        # Cada patrón tiene un peso implícito según tipo
        PATTERN_WEIGHTS = {
            "emotional_manipulation":    0.9,
            "overpromise":               0.85,
            "weak_scientific_basis":     0.8,
            "polarized_narrative":       0.75,
            "artificial_urgency":        0.7,
            "clickbait_pattern":         0.65,
            "weak_authority_claim":      0.6,
            "unverified_information":    0.55,
            "low_information_quality":   0.5,
            "no_pattern":                0.0,
        }

        if patterns:
            dominant = max(
                patterns,
                key=lambda p: PATTERN_WEIGHTS.get(p.get("type", ""), 0.3)
            )
            dominant = {**dominant, "weight": PATTERN_WEIGHTS.get(dominant.get("type",""), 0.3)}
        else:
            dominant = {
                "type": "no_pattern",
                "label": "Sin patrones críticos detectados",
                "explanation": "El contenido no presenta estructuras narrativas de riesgo significativas.",
                "weight": 0.0
            }

        # — Evidencia textual (frases del contenido) —
        def _collect_evidence(modules):
            ev = []
            for m in modules:
                if isinstance(m, dict):
                    ev.extend(m.get("evidence", []))
                else:
                    ev.extend(getattr(m, "evidence", []))
            return list(dict.fromkeys(ev))[:4]

        evidence_list = _collect_evidence([
            credibility, emotions, urgency, misinformation,
            scientific, narrative, promises, uncertainty
        ])

        # — Recomendación accionable —
        def _build_recommendation(risk_score, patterns, comm_data):
            comm_level = comm_data.get("level", "none")
            pattern_types = [p.get("type","") for p in patterns]

            if comm_level == "alto":
                return {
                    "action": "no_comprar",
                    "text": "Este sitio presenta múltiples señales de riesgo comercial. No ingreses datos de pago ni información personal."
                }
            if "emotional_manipulation" in pattern_types or "overpromise" in pattern_types:
                return {
                    "action": "verificar_fuentes",
                    "text": "Antes de compartir o actuar, buscá la fuente primaria. El contenido usa recursos emocionales o promesas que pueden distorsionar la percepción."
                }
            if "weak_scientific_basis" in pattern_types or "unsupported_scientific_claim" in pattern_types:
                return {
                    "action": "consultar_experto",
                    "text": "Las afirmaciones de salud o ciencia presentes no tienen respaldo verificable. Consultá fuentes académicas o profesionales antes de tomar decisiones."
                }
            if "polarized_narrative" in pattern_types:
                return {
                    "action": "buscar_otras_perspectivas",
                    "text": "El contenido presenta una visión polarizada. Buscá otras fuentes con perspectivas distintas antes de formarte una opinión."
                }
            if risk_score >= 0.20:
                return {
                    "action": "lectura_critica",
                    "text": "Leé con atención crítica. Algunas señales estructurales sugieren que el contenido puede estar diseñado para influir en tu percepción."
                }
            return {
                "action": "lectura_normal",
                "text": "No se detectan patrones de riesgo estructural significativos. Podés continuar con lectura normal."
            }

        recommendation = _build_recommendation(risk_score, patterns, comm_data)

        pro_block = {
            "dimensions": dimensions,
            "radar": {
                "emocional":    dim_emocional,
                "narrativo":    dim_narrativo,
                "credibilidad": dim_credibilidad,
                "cientifico":   dim_cientifico,
                "comercial":    dim_comercial,
            },
            "dominant_pattern": dominant,
            "evidence":         evidence_list,
            "recommendation":   recommendation,
            "insight":          insight,
            "context_note":     f"Análisis estructural en modo {context}",
        }

        return {
            "score":       int(round(risk_score * 100)),
            "level":       level,
            "message":     message,
            "signals":     adjusted_signals[:6],
            "confidence":  round(confidence, 2),
            "insight":     insight,
            "context":     context,
            "source_type": source_info.get("type", "unknown"),
            "commercial_risk": comm_data,
            "pro": pro_block
        }

    except Exception as e:
        print(f"CRITICAL ENGINE ERROR en {url}:")
        traceback.print_exc() 
        
        return {
            "score": 0,
            "level": "yellow", 
            "message": "No se pudo completar el análisis (error en el motor).",
            "signals": [f"Error interno: {str(e)}"],
            "confidence": 0,
            "insight": "Hubo un fallo al procesar la información de esta página.",
            "context": "error",
            "source_type": "unknown",
            "commercial_risk": {},
            "pro": {
                "error_trace": traceback.format_exc()
            }
        }