# ======================================================
# SIGNAL PRIORITIZATION LAYER v1
# ======================================================

def detect_content_type(text: str, url: str) -> str:

    text = text.lower()
    url = url.lower()

    # ecommerce
    if any(word in text for word in ["comprar", "oferta", "envío", "carrito"]):
        return "ecommerce"

    # institucional
    if ".gov" in url or ".edu" in url:
        return "institutional"

    # noticia
    if any(word in text for word in ["según", "informó", "reportó", "fuentes"]):
        return "news"

    return "generic"


# ------------------------------------------------------

def adjust_signals(signals: list, context: str):

    for s in signals:

        # Ecommerce → urgencia es normal
        if context == "ecommerce" and getattr(s, "type", "") == "urgency":
            s.points *= 0.3

        # Noticias → incertidumbre es saludable
        if context == "news" and getattr(s, "type", "") == "uncertainty":
            s.points *= 0.5

        # Institucional → bajar emocionalidad
        if context == "institutional" and getattr(s, "type", "") == "emotions":
            s.points *= 0.6

    return signals


# ------------------------------------------------------

def combo_boost(signals: list) -> float:

    types = [getattr(s, "type", "") for s in signals]

    bonus = 0.0

    if "urgency" in types and "emotions" in types:
        bonus += 0.15

    if "promises" in types and "credibility" in types:
        bonus += 0.20

    return bonus