# ======================================================
# SIGNALCHECK – TEXT NORMALIZER (PRO VERSION)
# ======================================================

import re


def normalize_text(text: str):

    if not text:
        return ""

    # Reemplazo de saltos y tabs
    text = text.replace("\n", " ").replace("\t", " ")

    # Eliminar múltiples espacios
    text = re.sub(r"\s+", " ", text)

    # Eliminar espacios al inicio y final
    text = text.strip()

    # Lowercase (importante para matching)
    text = text.lower()

    return text