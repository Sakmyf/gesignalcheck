# backend/Analysis/contradictions.py

import re


def analyze_contradictions(text: str) -> dict:
    """
    Detecta posibles contradicciones internas simples.
    """

    if not text:
        return {"score": 0.0, "signals": [], "evidence": []}

    text_lower = text.lower()

    negations = [
        "no hay evidencia",
        "no existe",
        "no está probado"
    ]

    affirmations = [
        "está demostrado",
        "es un hecho",
        "comprobado"
    ]

    found_neg = [p for p in negations if p in text_lower]
    found_aff = [p for p in affirmations if p in text_lower]

    score = 0.0
    signals = []
    evidence = []

    if found_neg and found_aff:
        score = 0.8
        signals.append("internal_contradiction")
        evidence.append(
            f"Posible contradicción: negación ({found_neg[0]}) + afirmación ({found_aff[0]})"
        )

    return {
        "score": round(score, 2),
        "signals": signals,
        "evidence": evidence
    }