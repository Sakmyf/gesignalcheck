# ======================================================
# SIGNALCHECK – PATTERN ENGINE v1.1 (ALINEADO)
# ======================================================

def detect_patterns(signals: list, risk_score: float):
    """
    Detecta patrones narrativos a partir de señales combinadas
    Interpretación de comportamiento (no keywords directas)
    """

    patterns = []
    s = set(signals)

    # --------------------------------------------------
    # 1. EMOCIÓN + FALTA DE EVIDENCIA
    # --------------------------------------------------
    if "emotional_intensity" in s and "unsupported_scientific_claim" in s:
        patterns.append({
            "type": "emotional_manipulation",
            "label": "Lenguaje emocional sin respaldo",
            "explanation": "Se apela a emociones fuertes sin evidencia suficiente"
        })

    # --------------------------------------------------
    # 2. AUTORIDAD DÉBIL + AFIRMACIONES FUERTES
    # --------------------------------------------------
    if "low_credibility_opinion" in s and "categorical_claim" in s:
        patterns.append({
            "type": "weak_authority_claim",
            "label": "Afirmaciones sin respaldo sólido",
            "explanation": "Se presentan conclusiones fuertes sin fuentes confiables"
        })

    # --------------------------------------------------
    # 3. CLICKBAIT (TÍTULO VS CONTENIDO)
    # --------------------------------------------------
    if "titular_exagerado" in s or "desfase_titular_contenido" in s:
        patterns.append({
            "type": "clickbait_pattern",
            "label": "Posible clickbait",
            "explanation": "El titular exagera o no coincide con el contenido"
        })

    # --------------------------------------------------
    # 4. NARRATIVA POLARIZADA
    # --------------------------------------------------
    if "polarization_detected" in s and "overgeneralization" in s:
        patterns.append({
            "type": "polarized_narrative",
            "label": "Narrativa polarizada",
            "explanation": "Se presenta una visión extrema sin matices"
        })

    # --------------------------------------------------
    # 5. URGENCIA ARTIFICIAL
    # --------------------------------------------------
    if "urgency_pressure" in s and risk_score > 0.5:
        patterns.append({
            "type": "artificial_urgency",
            "label": "Urgencia artificial",
            "explanation": "Se intenta generar presión para reaccionar rápido"
        })

    # --------------------------------------------------
    # 6. PROMESAS EXAGERADAS
    # --------------------------------------------------
    if "exaggerated_promises" in s:
        patterns.append({
            "type": "overpromise",
            "label": "Promesas exageradas",
            "explanation": "Se prometen resultados sin garantías reales"
        })

    # --------------------------------------------------
    # 7. CIENTIFICISMO DÉBIL
    # --------------------------------------------------
    if "unsupported_scientific_claim" in s:
        patterns.append({
            "type": "weak_scientific_basis",
            "label": "Base científica débil",
            "explanation": "Se usan términos científicos sin respaldo verificable"
        })

    # --------------------------------------------------
    # 8. CONTENIDO HIPOTÉTICO / NO VERIFICADO
    # --------------------------------------------------
    if "hypothetical_or_unverified_claim" in s:
        patterns.append({
            "type": "unverified_information",
            "label": "Información no verificada",
            "explanation": "Se presentan hechos sin confirmación clara"
        })

    # --------------------------------------------------
    # 9. BAJA CALIDAD INFORMATIVA GLOBAL
    # --------------------------------------------------
    if risk_score > 0.7 and len(s) > 3:
        patterns.append({
            "type": "low_information_quality",
            "label": "Calidad informativa baja",
            "explanation": "El contenido acumula múltiples señales de baja confiabilidad"
        })

    return patterns