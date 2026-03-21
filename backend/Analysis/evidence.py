# backend/Analysis/evidence.py

import re

def analyze_evidence(text: str) -> dict:
    """
    Evalúa la presencia de evidencia en el contenido.
    Score: 0.0 (sin evidencia) → 1.0 (alta evidencia)
    """

    if not text:
        return {"score": 0.0, "signals": []}

    text_lower = text.lower()

    score = 0.0
    signals = []

    # 🔢 Presencia de números (datos concretos)
    numbers = re.findall(r"\d+", text)
    if len(numbers) >= 3:
        score += 0.25
        signals.append("datos_numéricos")

    # 📊 Referencias a estudios / fuentes
    source_patterns = [
        "estudio", "investigación", "paper",
        "según", "de acuerdo a", "informe",
        "publicado en", "journal"
    ]

    if any(p in text_lower for p in source_patterns):
        score += 0.25
        signals.append("referencia_fuente")

    # 🔗 URLs o citas externas
    if "http://" in text_lower or "https://" in text_lower:
        score += 0.2
        signals.append("links_externos")

    # 👨‍🔬 Autoridad concreta (con nombre)
    if re.search(r"\b(dr\.|doctor|profesor|científico)\b", text_lower):
        score += 0.15
        signals.append("autoridad_nominal")

    # 🚫 Penalización: afirmaciones sin respaldo
    weak_patterns = [
        "expertos dicen",
        "muchos creen",
        "se dice que",
        "algunos afirman"
    ]

    if any(p in text_lower for p in weak_patterns):
        score -= 0.2
        signals.append("afirmación_sin_respaldo")

    score = max(0.0, min(score, 1.0))

    return {
        "score": round(score, 2),
        "signals": signals
    }