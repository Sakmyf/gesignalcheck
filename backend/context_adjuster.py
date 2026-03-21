# ======================================================
# SIGNALCHECK – CONTEXT ADJUSTER v1.0
# Ajusta señales según contexto
# ======================================================

def adjust_signals_by_context(signals: list, context: str):
    """
    Ajusta señales para evitar falsos positivos
    """

    adjusted = []

    for s in signals:

        # --------------------------------------------------
        # SALUD: "cura" no es automáticamente sospechoso
        # --------------------------------------------------
        if context == "health_science":
            if s == "absolute_claims":
                continue  # se relaja

        # --------------------------------------------------
        # NOTICIAS: confianza base mayor
        # --------------------------------------------------
        if context == "news":
            if s == "lack_of_evidence":
                continue

        adjusted.append(s)

    return adjusted