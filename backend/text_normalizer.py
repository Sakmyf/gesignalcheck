# ======================================================
# SIGNALCHECK – TEXT NORMALIZER
# ======================================================

def normalize_text(text: str):
    if not text:
        return ""

    return (
        text.replace("\n", " ")
            .replace("\t", " ")
            .strip()
            .lower()
    )