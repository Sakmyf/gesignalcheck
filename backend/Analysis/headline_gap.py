# backend/Analysis/headline_gap.py

def analyze_headline_gap(headline: str, body: str) -> dict:
    """
    Detecta diferencia entre intensidad del titular y el contenido.
    """

    if not headline or not body:
        return {"gap_score": 0.0, "signals": []}

    headline = headline.lower()
    body = body.lower()

    hype_words = [
        "impactante", "increíble", "nunca visto",
        "revolucionario", "escándalo", "urgente"
    ]

    moderation_words = [
        "podría", "posible", "preliminar",
        "en estudio", "según", "indicios"
    ]

    hype_count = sum(1 for w in hype_words if w in headline)
    moderation_count = sum(1 for w in moderation_words if w in body)

    gap_score = 0.0
    signals = []

    if hype_count > 0 and moderation_count > 0:
        gap_score = 0.7
        signals.append("desfase_titular_contenido")

    elif hype_count > 0:
        gap_score = 0.5
        signals.append("titular_exagerado")

    return {
        "gap_score": gap_score,
        "signals": signals
    }