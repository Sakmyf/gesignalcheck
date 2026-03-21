# ======================================================
# SIGNALCHECK – PATTERN ENGINE v1.0
# Capa de interpretación narrativa
# ======================================================

def detect_patterns(signals: list, risk_score: float):
    """
    Detecta patrones narrativos a partir de señales combinadas
    NO detecta keywords → interpreta comportamiento global
    """

    patterns = []
    s = set(signals)

    # --------------------------------------------------
    # 1. EMOCIÓN + FALTA DE EVIDENCIA
    # --------------------------------------------------
    if "emotional_language" in s and "lack_of_evidence" in s:
        patterns.append({
            "type": "emotional_manipulation",
            "label": "Lenguaje emocional sin respaldo",
            "explanation": "El contenido apela a emociones pero no presenta evidencia clara"
        })

    # --------------------------------------------------
    # 2. AUTORIDAD DÉBIL + AFIRMACIONES FUERTES
    # --------------------------------------------------
    if "weak_authority" in s and "absolute_claims" in s:
        patterns.append({
            "type": "weak_authority_claim",
            "label": "Afirmaciones sin respaldo sólido",
            "explanation": "Se presentan conclusiones fuertes sin fuentes confiables"
        })

    # --------------------------------------------------
    # 3. CLICKBAIT (TÍTULO VS CONTENIDO)
    # --------------------------------------------------
    if "headline_exaggeration" in s and "content_mismatch" in s:
        patterns.append({
            "type": "clickbait_pattern",
            "label": "Posible clickbait",
            "explanation": "El título promete más de lo que el contenido desarrolla"
        })

    # --------------------------------------------------
    # 4. NARRATIVA POLARIZADA
    # --------------------------------------------------
    if "polarized_language" in s and "lack_of_balance" in s:
        patterns.append({
            "type": "polarized_narrative",
            "label": "Narrativa polarizada",
            "explanation": "Se presenta una única perspectiva sin contraste"
        })

    # --------------------------------------------------
    # 5. URGENCIA ARTIFICIAL
    # --------------------------------------------------
    if "urgency_language" in s and risk_score > 0.5:
        patterns.append({
            "type": "artificial_urgency",
            "label": "Urgencia artificial",
            "explanation": "Se intenta generar presión para una reacción inmediata"
        })

    # --------------------------------------------------
    # 6. PROMESAS EXAGERADAS + POCA BASE
    # --------------------------------------------------
    if "exaggerated_promises" in s and "lack_of_evidence" in s:
        patterns.append({
            "type": "overpromise_without_support",
            "label": "Promesas sin sustento",
            "explanation": "Se prometen resultados sin justificar cómo se logran"
        })

    # --------------------------------------------------
    # 7. CIENTIFICISMO DÉBIL
    # --------------------------------------------------
    if "scientific_claims" in s and "weak_authority" in s:
        patterns.append({
            "type": "weak_scientific_basis",
            "label": "Base científica débil",
            "explanation": "Se usan términos científicos sin respaldo verificable"
        })

    # --------------------------------------------------
    # 8. CONTRADICCIONES INTERNAS
    # --------------------------------------------------
    if "internal_contradiction" in s:
        patterns.append({
            "type": "contradictory_content",
            "label": "Posibles contradicciones",
            "explanation": "El contenido presenta inconsistencias internas"
        })

    # --------------------------------------------------
    # 9. BAJA CALIDAD INFORMATIVA (GLOBAL)
    # --------------------------------------------------
    if risk_score > 0.7 and len(s) > 3:
        patterns.append({
            "type": "low_information_quality",
            "label": "Calidad informativa baja",
            "explanation": "El contenido presenta múltiples señales de baja confiabilidad"
        })

    return patterns