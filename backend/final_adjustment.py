# ==========================================================
# FINAL ADJUSTMENT LAYER
# Opera sobre el resultado del engine antes de construir
# la respuesta final. No modifica scores.
# FIX P0: leer "signals" (clave real del engine, no "reasons"/"indicators")
# ==========================================================

SUMMARY_MAP = {
    ("green",  ""):          "El contenido no presenta patrones estructurales de riesgo.",
    ("yellow", ""):          "El contenido requiere lectura crítica.",
    ("red",    ""):          "Se detectó presión narrativa significativa.",
    ("green",  "recreado"):  "Contenido posiblemente recreado. Verificá las fuentes.",
    ("yellow", "recreado"):  "Contenido con indicios de reconstrucción no verificable.",
    ("red",    "recreado"):  "Alta presión narrativa con indicios de reconstrucción.",
    ("green",  "emocional"): "Contenido con carga emocional. Verificá las fuentes.",  # FIX: entrada faltante
    ("yellow", "emocional"): "Lenguaje con carga emocional elevada.",
    ("red",    "emocional"): "Alta presión emocional y narrativa combinadas.",
}

# Palabras clave a buscar en los signals del engine
_RECONSTRUCTION_KEYWORDS = ("reconstrucción", "recreado", "dramatizada", "hypothetical")
_EMOTIONAL_KEYWORDS       = ("emocional", "emoción", "emotion", "urgency_pressure")


def apply_context_adjustment(result: dict) -> dict:

    # FIX P0: el engine devuelve "signals", no "reasons" ni "indicators"
    signals = result.get("signals", [])

    has_reconstruction = any(
        any(kw in s.lower() for kw in _RECONSTRUCTION_KEYWORDS)
        for s in signals
    )
    has_emotional = any(
        any(kw in s.lower() for kw in _EMOTIONAL_KEYWORDS)
        for s in signals
    )

    current_level = result.get("level", "yellow")

    if has_reconstruction:
        if current_level == "green":
            result["level"] = "yellow"
        result["context_note"] = "contenido posiblemente recreado o no verificable"

    elif has_emotional:
        result["context_note"] = "carga emocional narrativa detectada"

    else:
        result["context_note"] = ""

    return result


def build_summary(result: dict) -> str:

    status = result.get("level", "yellow")
    note   = result.get("context_note", "")

    if "recreado" in note or "reconstrucción" in note:
        context_key = "recreado"
    elif "emocional" in note:
        context_key = "emocional"
    else:
        context_key = ""

    return SUMMARY_MAP.get(
        (status, context_key),
        result.get("message", "Análisis completado.")
    )
