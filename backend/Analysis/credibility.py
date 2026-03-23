# backend/Analysis/credibility.py

import re
from backend.Analysis.rules_types import RuleResult


SOURCE_PATTERNS = [
    r"según",
    r"dijo",
    r"informó",
    r"declaró",
    r"reportó",
    r"informe",
    r"de acuerdo con",
]

DATA_PATTERNS = [
    r"\d+%",       # porcentaje
    r"\d{4}",      # años
    r"\d+\.\d+",   # decimales
]

OPINION_PATTERNS = [
    r"creo que",
    r"me parece",
    r"es evidente que",
    r"sin dudas",
]


def check_credibility(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    found_sources = [p for p in SOURCE_PATTERNS if re.search(p, text_lower)]
    found_data = [p for p in DATA_PATTERNS if re.search(p, text_lower)]
    found_opinions = [p for p in OPINION_PATTERNS if re.search(p, text_lower)]

    has_source = bool(found_sources)
    has_data = bool(found_data)
    has_opinion = bool(found_opinions)

    # ======================================================
    # 🔴 Opinión fuerte sin respaldo
    # Antes: +0.9 → Ahora: +0.35
    # Requiere al menos 2 patrones para activarse fuerte
    # ======================================================

    if has_opinion and not has_source and not has_data:
        opinion_count = len(found_opinions)
        score = 0.2 if opinion_count == 1 else 0.35
        result.points += score
        result.reasons.append("low_credibility_opinion")
        result.evidence.append(
            f"Opinión sin respaldo detectada ({', '.join(found_opinions)})"
        )

    # ======================================================
    # 🟠 Sin fuentes detectadas
    # Antes: +0.5 → Ahora: +0.15
    # La ausencia de "según" no es evidencia de riesgo por sí sola
    # ======================================================

    elif not has_source:
        result.points += 0.15
        result.reasons.append("no_detected_source")
        result.evidence.append("No se detectaron fuentes explícitas")

    # ======================================================
    # 🟢 Bonus: contenido con fuentes + datos
    # ======================================================

    if has_source and has_data:
        result.points -= 0.15
        result.reasons.append("supported_information")
        result.evidence.append("Contenido con fuentes y datos detectados")

    # ======================================================
    # LIMPIEZA
    # ======================================================

    result.points = max(0.0, result.points)
    result.reasons = list(dict.fromkeys(result.reasons))
    result.evidence = list(dict.fromkeys(result.evidence))

    return result


def analyze(text: str):
    return check_credibility(text)