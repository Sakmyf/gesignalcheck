# ==========================================================
# FINAL ADJUSTMENT LAYER
# Opera sobre el resultado del engine antes de construir
# la respuesta final. No modifica scores ni signals.
# ==========================================================

SUMMARY_MAP = {
    ("green",  ""):          "El contenido no presenta patrones estructurales de riesgo.",
    ("yellow", ""):          "El contenido requiere lectura crítica.",
    ("red",    ""):          "Se detectó presión narrativa significativa.",
    ("green",  "recreado"):  "Contenido posiblemente recreado. Verificá las fuentes.",
    ("yellow", "recreado"):  "Contenido con indicios de reconstrucción no verificable.",
    ("red",    "recreado"):  "Alta presión narrativa con indicios de reconstrucción.",
    ("yellow", "emocional"): "Lenguaje con carga emocional elevada.",
    ("red",    "emocional"): "Alta presión emocional y narrativa combinadas.",
}


def apply_context_adjustment(result: dict) -> dict:

    reasons    = result.get("reasons", [])
    indicators = result.get("indicators", [])

    has_reconstruction = any("reconstrucción" in r for r in reasons)
    has_dramatization  = any("dramatizada" in r for r in reasons)
    has_emotional      = any("emocional" in r for r in reasons)

    has_indicator_flag = any(
        "reconstrucción" in i.get("title", "").lower() or
        "dramatizada" in i.get("title", "").lower()
        for i in indicators
        if isinstance(i, dict)
    )

    # =========================================
    # FIX: usar "level" (clave real del engine)
    # antes usaba "status" → siempre None → bug silencioso
    # =========================================

    current_level = result.get("level", result.get("status", "yellow"))

    if has_reconstruction or has_dramatization or has_indicator_flag:
        if current_level == "green":
            result["level"] = "yellow"
            result["label"] = "requiere lectura crítica"
        result["context_note"] = "contenido posiblemente recreado o no verificable"

    elif has_emotional:
        result["context_note"] = "carga emocional narrativa detectada"

    else:
        result["context_note"] = ""

    return result


def build_summary(result: dict) -> str:

    # FIX: leer "level" en lugar de "status"
    status = result.get("level", result.get("status", "yellow"))
    note   = result.get("context_note", "")

    if "recreado" in note or "reconstrucción" in note:
        context_key = "recreado"
    elif "emocional" in note:
        context_key = "emocional"
    else:
        context_key = ""

    return SUMMARY_MAP.get(
        (status, context_key),
        result.get("message", result.get("label", "Análisis completado."))
    )