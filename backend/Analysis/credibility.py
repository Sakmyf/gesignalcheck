# ======================================================
# SIGNALCHECK – CREDIBILITY ANALYZER PRO v2 (REAL WORLD)
# ======================================================

import re

def analyze(text: str):

    if not text:
        return {"score": 0.0, "signals": []}

    text_lower = text.lower()

    score = 0.0
    signals = []

    # ======================================================
    # DETECCIÓN EMOCIONAL (AMPLIADA)
    # ======================================================

    emotional_words = [
        "increible", "impactante", "brutal", "terrible",
        "impresionante", "explota", "escandalo",
        "shock", "indignacion", "caos", "furia"
    ]

    emotional_hits = sum(1 for w in emotional_words if w in text_lower)

    if emotional_hits > 0:
        score += min(0.1 * emotional_hits, 0.4)
        signals.append("lenguaje emocional")

    # ======================================================
    # DRAMATIZACIÓN (CLAVE)
    # ======================================================

    drama_patterns = [
        "no podia creer",
        "quedo en shock",
        "dejo paralizada",
        "genero caos",
        "nadie lo esperaba",
        "todo cambio",
        "situacion tensa",
    ]

    drama_hits = sum(1 for p in drama_patterns if p in text_lower)

    if drama_hits > 0:
        score += min(0.15 * drama_hits, 0.4)
        signals.append("dramatizacion")

    # ======================================================
    # STORYTELLING NARRATIVO (MUY IMPORTANTE)
    # ======================================================

    storytelling_patterns = [
        "con esta frase",
        "lo que parecia",
        "en ese momento",
        "de repente",
        "finalmente",
        "dentro de este relato",
    ]

    story_hits = sum(1 for p in storytelling_patterns if p in text_lower)

    if story_hits >= 1:
        score += 0.2
        signals.append("estructura narrativa")

    # ======================================================
    # FRASES LARGAS (SEÑAL REAL DE STORYTELLING)
    # ======================================================

    sentences = text.split(".")
    long_sentences = [s for s in sentences if len(s.split()) > 20]

    if len(long_sentences) >= 2:
        score += 0.15
        signals.append("narrativa extensa")

    # ======================================================
    # EXCESO DE ADJETIVOS (heurística fuerte)
    # ======================================================

    adjectives = [
        "increible", "impactante", "terrible", "impresionante",
        "inesperado", "fuerte", "brutal"
    ]

    adj_hits = sum(1 for w in adjectives if w in text_lower)

    if adj_hits >= 2:
        score += 0.15
        signals.append("exceso de adjetivos")

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    score = max(0.0, min(score, 1.0))

    return {
        "score": score,
        "signals": signals
    }