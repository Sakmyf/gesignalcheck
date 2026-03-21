# backend/Analysis/contradictions.py

import re

def analyze_contradictions(text: str) -> dict:
    """
    Detecta posibles contradicciones internas simples.
    """

    if not text:
        return {"score": 0.0, "signals": []}

    text_lower = text.lower()

    negations = ["no hay evidencia", "no existe", "no está probado"]
    affirmations = ["está demostrado", "es un hecho", "comprobado"]

    found_neg = any(p in text_lower for p in negations)
    found_aff = any(p in text_lower for p in affirmations)

    score = 0.0
    signals = []

    if found_neg and found_aff:
        score = 0.8
        signals.append("posible_contradicción")

    return {
        "score": score,
        "signals": signals
    }