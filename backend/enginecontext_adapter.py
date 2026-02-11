def adapt_context(ai_ctx: dict):
    """
    Traduce contexto IA a score interpretativo.

    Principios:
    - NO penaliza lenguaje normal en medios periodísticos.
    - El score solo sube cuando hay RIESGO REAL.
    - El tono por sí solo NO vuelve falso un contenido.
    - El contexto editorial se detecta por señales, no por listas.
    """

    score = 0
    signals = []

    page_type = ai_ctx.get("page_type", "unknown")
    tone = ai_ctx.get("tone", "neutral")
    risk = ai_ctx.get("risk_level", "low")

    # ======================================================
    # 📰 DETECCIÓN DE CONTEXTO EDITORIAL GLOBAL
    # ======================================================
    is_editorial = False

    editorial_signals = [
        ai_ctx.get("has_author"),
        ai_ctx.get("has_date"),
        ai_ctx.get("has_sections"),
        ai_ctx.get("has_legal_links"),
        ai_ctx.get("is_news_domain"),
    ]

    if sum(1 for s in editorial_signals if s) >= 3:
        is_editorial = True
        signals.append("Contexto editorial detectado")

    # ======================================================
    # 🟢 CONTEXTO ATENUANTE (INFORMATIVO)
    # ======================================================
    if page_type == "institutional":
        signals.append("Fuente institucional")

    if page_type in ("news", "news_editorial", "news_economy") or is_editorial:
        signals.append("Contenido periodístico")

    # ======================================================
    # 🟡 ESTILO DEL LENGUAJE (NO SIEMPRE RIESGO)
    # ======================================================
    if tone == "emotional":
        if is_editorial:
            signals.append("Lenguaje enfático típico del periodismo")
        else:
            score += 1
            signals.append("Lenguaje emocional fuera de contexto informativo")

    if tone == "alarmist":
        if is_editorial:
            signals.append("Énfasis periodístico en escenarios o alertas")
        else:
            score += 2
            signals.append("Tono alarmista sin respaldo contextual")

    # ======================================================
    # 🟡 RIESGO CONTEXTUAL (INTERPRETACIÓN)
    # ======================================================
    if risk == "medium":
        if is_editorial:
            signals.append("Análisis con proyecciones o escenarios posibles")
        else:
            score += 1
            signals.append("Información con interpretación ambigua")

    # ======================================================
    # 🔴 RIESGO REAL (POCO FRECUENTE)
    # ======================================================
    if risk == "high":
        score += 3
        signals.append("Alto riesgo contextual detectado")

    # ======================================================
    # ℹ️ SEÑALES ADICIONALES (NO SUMAN SCORE)
    # ======================================================
    for s in ai_ctx.get("authority_signals", []):
        signals.append(s)

    for s in ai_ctx.get("caution_signals", []):
        signals.append(s)

    return score, signals

