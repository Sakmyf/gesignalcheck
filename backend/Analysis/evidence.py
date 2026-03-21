# backend/Analysis/evidence.py

import re


def analyze_evidence(text: str) -> dict:
    """
    Evalúa la presencia de evidencia en el contenido.
    Score: 0.0 (sin evidencia) → 1.0 (alta evidencia)
    """

    if not text:
        return {"score": 0.0, "signals": [], "evidence": []}

    text_lower = text.lower()

    score = 0.0
    signals = []
    evidence = []

    # ======================================================
    # 🔢 DATOS NUMÉRICOS
    # ======================================================

    numbers = re.findall(r"\d+", text)

    if len(numbers) >= 3:
        score += 0.25
        signals.append("datos_numericos")
        evidence.append(f"Se detectaron {len(numbers)} valores numéricos")

    # ======================================================
    # 📊 REFERENCIAS A FUENTES
    # ======================================================

    source_patterns = [
        "estudio", "investigación", "paper",
        "según", "de acuerdo a", "informe",
        "publicado en", "journal"
    ]

    found_sources = [p for p in source_patterns if p in text_lower]

    if found_sources:
        score += 0.25
        signals.append("referencia_fuente")
        evidence.append(
            f"Referencia a fuente detectada: {', '.join(found_sources[:3])}"
        )

    # ======================================================
    # 🔗 LINKS EXTERNOS
    # ======================================================

    if "http://" in text_lower or "https://" in text_lower:
        score += 0.2
        signals.append("links_externos")
        evidence.append("Se detectaron enlaces externos")

    # ======================================================
    # 👨‍🔬 AUTORIDAD NOMINAL
    # ======================================================

    if re.search(r"\b(dr\.|doctor|profesor|científico)\b", text_lower):
        score += 0.15
        signals.append("autoridad_nominal")
        evidence.append("Se menciona una figura de autoridad")

    # ======================================================
    # 🚫 AFIRMACIONES DÉBILES (PENALIZACIÓN)
    # ======================================================

    weak_patterns = [
        "expertos dicen",
        "muchos creen",
        "se dice que",
        "algunos afirman"
    ]

    found_weak = [p for p in weak_patterns if p in text_lower]

    if found_weak:
        score -= 0.2
        signals.append("afirmacion_sin_respaldo")
        evidence.append(
            f"Afirmaciones débiles detectadas: {', '.join(found_weak)}"
        )

    # ======================================================
    # NORMALIZACIÓN
    # ======================================================

    score = max(0.0, min(score, 1.0))

    # evitar duplicados
    signals = list(dict.fromkeys(signals))
    evidence = list(dict.fromkeys(evidence))

    return {
        "score": round(score, 2),
        "signals": signals,
        "evidence": evidence
    }