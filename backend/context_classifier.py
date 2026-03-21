# ======================================================
# SIGNALCHECK – CONTEXT CLASSIFIER v1.0
# Detecta el tipo de contenido
# ======================================================

def classify_context(text: str):
    """
    Clasifica el tipo de contenido para ajustar interpretación
    """

    t = text.lower()

    # --------------------------------------------------
    # SALUD / CIENCIA
    # --------------------------------------------------
    if any(word in t for word in [
        "estudio", "científico", "investigación", "ensayo",
        "salud", "medicina", "tratamiento", "enfermedad"
    ]):
        return "health_science"

    # --------------------------------------------------
    # POLÍTICA
    # --------------------------------------------------
    if any(word in t for word in [
        "gobierno", "presidente", "elecciones",
        "congreso", "política", "ley"
    ]):
        return "politics"

    # --------------------------------------------------
    # OPINIÓN / EDITORIAL
    # --------------------------------------------------
    if any(word in t for word in [
        "opinión", "creo", "pienso", "desde mi punto de vista"
    ]):
        return "opinion"

    # --------------------------------------------------
    # NOTICIA GENERAL
    # --------------------------------------------------
    if any(word in t for word in [
        "informó", "según", "reportó", "declaró"
    ]):
        return "news"

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------
    return "general"