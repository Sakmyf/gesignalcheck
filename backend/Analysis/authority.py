# backend/Analysis/authority.py

def analyze_authority(text: str) -> dict:
    """
    Detecta uso indebido o válido de autoridad en el contenido.
    """

    if not text:
        return {"score": 0.0, "signals": [], "evidence": []}

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
    evidence = []

    found_weak = [p for p in weak_authority if p in text_lower]
    found_strong = [p for p in strong_authority if p in text_lower]

    # --------------------------------------------------
    # 🔴 AUTORIDAD DÉBIL
    # --------------------------------------------------
    if found_weak:
        score += 0.6
        signals.append("weak_authority")
        evidence.append(
            f"Autoridad difusa detectada: {', '.join(found_weak)}"
        )

    # --------------------------------------------------
    # 🟢 AUTORIDAD FUERTE
    # --------------------------------------------------
    if found_strong:
        score -= 0.3
        signals.append("strong_authority")
        evidence.append(
            f"Referencia a autoridad concreta: {', '.join(found_strong[:2])}"
        )

    # --------------------------------------------------
    # NORMALIZACIÓN
    # --------------------------------------------------
    score = max(0.0, min(score, 1.0))

    signals = list(dict.fromkeys(signals))
    evidence = list(dict.fromkeys(evidence))

    return {
        "score": round(score, 2),
        "signals": signals,
        "evidence": evidence
    }