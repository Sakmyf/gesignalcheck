# backend/Analysis/authority.py
# FIX P0: separar riesgo (autoridad débil) de reducción (autoridad fuerte)
# en dos campos distintos para que el engine los aplique correctamente.


def analyze_authority(text: str) -> dict:
    """
    Detecta uso de autoridad en el contenido.

    Retorna dos campos separados:
      score       → contribución de RIESGO (autoridad vaga, sin referente)
      trust_bonus → reducción de riesgo (autoridad concreta y verificable)
    """

    if not text:
        return {"score": 0.0, "trust_bonus": 0.0, "signals": [], "evidence": []}

    text_lower = text.lower()

    weak_authority = [
        "expertos dicen",
        "científicos aseguran",
        "especialistas afirman",
        "según expertos",
    ]

    strong_authority = [
        "dr.", "doctor", "profesor",
        "universidad", "instituto",
    ]

    score       = 0.0   # riesgo (autoridad débil)
    trust_bonus = 0.0   # reducción de riesgo (autoridad fuerte)
    signals = []
    evidence = []

    found_weak   = [p for p in weak_authority   if p in text_lower]
    found_strong = [p for p in strong_authority if p in text_lower]

    # --------------------------------------------------
    # AUTORIDAD DÉBIL → agrega riesgo
    # Solo activa si no hay ningún referente concreto.
    # --------------------------------------------------
    if found_weak and not found_strong:
        score = 0.25
        signals.append("weak_authority")
        evidence.append(
            f"Autoridad difusa sin referente concreto: {', '.join(found_weak)}"
        )

    # --------------------------------------------------
    # AUTORIDAD FUERTE → reduce riesgo (trust_bonus)
    # FIX: antes se restaba al score y max(0) lo borraba.
    # Ahora es un campo separado que el engine resta explícitamente.
    # --------------------------------------------------
    if found_strong and not found_weak:
        trust_bonus = 0.15
        signals.append("strong_authority")
        evidence.append(
            f"Referencia a autoridad concreta: {', '.join(found_strong[:2])}"
        )
    elif found_strong and found_weak:
        # Tiene referentes concretos pero también vaguedad → beneficio parcial
        trust_bonus = 0.08
        signals.append("mixed_authority")
        evidence.append("Mezcla de autoridad difusa y concreta")

    signals = list(dict.fromkeys(signals))
    evidence = list(dict.fromkeys(evidence))

    return {
        "score":       round(score, 2),
        "trust_bonus": round(trust_bonus, 2),
        "signals":     signals,
        "evidence":    evidence,
    }
