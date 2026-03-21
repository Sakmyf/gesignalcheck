# backend/Analysis/framing.py

def analyze_framing(text: str) -> dict:
    """
    Relación emocionalidad vs contenido factual.
    """

    if not text:
        return {"score": 0.0, "signals": []}

    text_lower = text.lower()

    emotional_words = [
        "impactante", "alarmante", "terrible",
        "increíble", "indignante", "escandaloso"
    ]

    factual_words = [
        "datos", "porcentaje", "estudio",
        "informe", "análisis", "resultado"
    ]

    emotional_count = sum(text_lower.count(w) for w in emotional_words)
    factual_count = sum(text_lower.count(w) for w in factual_words)

    signals = []
    score = 0.0

    if emotional_count > factual_count:
        score = min(1.0, (emotional_count - factual_count) * 0.2)
        signals.append("dominancia_emocional")

    elif factual_count > emotional_count:
        signals.append("contenido_factual")

    return {
        "score": round(score, 2),
        "signals": signals
    }