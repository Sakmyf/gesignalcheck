# ======================================================
# SIGNALCHECK – CREDIBILITY ANALYZER PRO v1.0
# Detecta narrativa emocional, exageración y fake patterns
# ======================================================

import re

# ======================================================
# PATRONES CLAVE
# ======================================================

EMOTIONAL_PATTERNS = [
    r"incre[ií]ble",
    r"impactante",
    r"no lo vas a creer",
    r"te va a sorprender",
    r"brutal",
    r"explota",
    r"estall[oó]",
    r"esc[aá]ndalo",
]

DRAMA_PATTERNS = [
    r"no pod[ií]a creer",
    r"qued[oó] en shock",
    r"paraliz[ao]",
    r"nadie lo esperaba",
    r"todo cambi[oó]",
    r"gener[oó] caos",
]

STORYTELLING_PATTERNS = [
    r"con esta frase",
    r"lo que parec[ií]a",
    r"todo comenz[oó]",
    r"en ese momento",
    r"de repente",
    r"finalmente",
]

ABSOLUTE_PATTERNS = [
    r"todos",
    r"nadie",
    r"siempre",
    r"nunca",
    r"definitivamente",
    r"sin dudas",
]

# ======================================================
# ANALIZADOR PRINCIPAL
# ======================================================

def analyze(text: str):

    if not text:
        return {
            "score": 0.0,
            "signals": []
        }

    text = text.lower()

    score = 0.0
    signals = []

    # ======================================================
    # EMOCIONALIDAD
    # ======================================================

    emotional_hits = sum(len(re.findall(p, text)) for p in EMOTIONAL_PATTERNS)

    if emotional_hits > 0:
        score += min(emotional_hits * 0.08, 0.25)
        signals.append("lenguaje emocional")

    # ======================================================
    # DRAMATIZACIÓN
    # ======================================================

    drama_hits = sum(len(re.findall(p, text)) for p in DRAMA_PATTERNS)

    if drama_hits > 0:
        score += min(drama_hits * 0.1, 0.3)
        signals.append("dramatización narrativa")

    # ======================================================
    # STORYTELLING SOSPECHOSO
    # ======================================================

    story_hits = sum(len(re.findall(p, text)) for p in STORYTELLING_PATTERNS)

    if story_hits >= 2:
        score += 0.15
        signals.append("estructura narrativa artificial")

    # ======================================================
    # ABSOLUTOS (SEÑAL CLAVE)
    # ======================================================

    absolute_hits = sum(len(re.findall(p, text)) for p in ABSOLUTE_PATTERNS)

    if absolute_hits > 1:
        score += 0.1
        signals.append("afirmaciones absolutas")

    # ======================================================
    # TEXTO MUY CARGADO (heurística real)
    # ======================================================

    if len(text) > 400 and (emotional_hits + drama_hits) > 2:
        score += 0.15
        signals.append("narrativa cargada")

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    score = max(0.0, min(score, 1.0))

    return {
        "score": score,
        "signals": signals
    }