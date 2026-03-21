# backend/Analysis/authority.py

def analyze_authority(text: str) -> dict:
    """
    Detecta uso indebido de autoridad sin respaldo concreto.
    """

    if not text:
        return {"score": 0.0, "signals": []}

    text_lower = text.lower()

    weak_authority = [
        "expertos dicen",
        "científicos aseguran",
        "especialistas afirman",
        "según expertos"
    ]

    strong_authority = [
        "dr.", "doctor", "profesor",
        "universidad", "instituto"
    ]

    score = 0.0
    signals = []

    if any(p in text_lower for p in weak_authority):
        score += 0.6
        signals.append("autoridad_difusa")

    if any(p in text_lower for p in strong_authority):
        score -= 0.3
        signals.append("autoridad_específica")

    score = max(0.0, min(score, 1.0))

    return {
        "score": round(score, 2),
        "signals": signals
    }