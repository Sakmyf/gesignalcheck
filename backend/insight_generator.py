# ======================================================
# SIGNALCHECK – INSIGHT GENERATOR v1.0
# Genera una lectura clara para humanos
# ======================================================

def generate_insight(patterns: list, profile: dict):
    """
    Genera una frase clara y directa para el usuario
    """

    if not patterns:
        return "El contenido no presenta señales relevantes de manipulación o riesgo."

    # --------------------------------------------------
    # BASE: tomar el patrón más fuerte
    # --------------------------------------------------
    main_pattern = patterns[0]["label"].lower()

    emocionalidad = profile.get("emocionalidad", 0)
    manipulacion = profile.get("manipulacion", 0)
    confiabilidad = profile.get("confiabilidad", 1)

    parts = []

    # --------------------------------------------------
    # EMOCIONALIDAD
    # --------------------------------------------------
    if emocionalidad > 0.6:
        parts.append("alto contenido emocional")

    elif emocionalidad > 0.3:
        parts.append("cierta carga emocional")

    # --------------------------------------------------
    # MANIPULACIÓN
    # --------------------------------------------------
    if manipulacion > 0.6:
        parts.append("posible enfoque manipulativo")

    elif manipulacion > 0.3:
        parts.append("algunos elementos persuasivos")

    # --------------------------------------------------
    # CONFIABILIDAD
    # --------------------------------------------------
    if confiabilidad < 0.4:
        parts.append("baja confiabilidad")

    elif confiabilidad < 0.7:
        parts.append("confiabilidad moderada")

    # --------------------------------------------------
    # CONSTRUCCIÓN FINAL
    # --------------------------------------------------
    if parts:
        summary = ", ".join(parts)
        return f"Contenido con {summary}. Detectado: {main_pattern}."
    else:
        return f"Se detecta: {main_pattern}."