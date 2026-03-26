# ======================================================
# SIGNALCHECK — DETECT UNCERTAINTY v1.0
# Detecta incertidumbre estructural en el contenido.
#
# Principio: ninguna de estas señales indica manipulación.
# Indican que el contenido no puede confirmarse con la
# información disponible en el texto.
#
# Efecto en score: empuja hacia amarillo (0.35–0.55).
# Nunca dispara rojo por sí solo.
# ======================================================

import re
from backend.Analysis.rules_types import RuleResult


NUMBER_PATTERNS = [
    r"\b\d+[\.,]?\d*\s*(mil|millones?|billones?|personas?|empleos?|puestos?|casos?|muertes?|contagios?)\b",
    r"\b\d+\s*%",
    r"\b\d+\s*de\s*cada\s*\d+\b",
]

SOURCE_INDICATORS = [
    r"\bsegún\b", r"\bde acuerdo\b", r"\binforme\b",
    r"\bestudio\b", r"\binvestigación\b", r"\bdatos?\b",
    r"\bcenso\b", r"\bindec\b", r"\bcepal\b", r"\boms\b",
    r"\bpublicado\b", r"\bfuente\b", r"\bcitó\b",
]

CONDITIONAL_PATTERNS = [
    r"\bhabría\b", r"\bhabrían\b",
    r"\bsería\b", r"\bserían\b",
    r"\bestaría\b", r"\bestarían\b",
    r"\bpodría\b", r"\bpodrían\b",
    r"\bdebería\b", r"\bdeberían\b",
    r"\btrascendió\b", r"\bse supo\b",
    r"\bse conoció\b", r"\bse especula\b",
    r"\bfuentes cercanas\b", r"\bfuentes confiables\b",
    r"\bsegún trascendió\b",
]

CATEGORICAL_UNVERIFIED = [
    r"\bes el peor\b", r"\bes el mejor\b",
    r"\bnunca antes\b", r"\bjamás\b",
    r"\bhistórico\b", r"\bsin precedentes\b",
    r"\bla mayor\b", r"\bla menor\b",
    r"\bcompletamente\b", r"\btotalmente\b",
    r"\bde forma definitiva\b",
]

RECENCY_PATTERNS = [
    r"\bhoy\b", r"\bayer\b", r"\banoche\b",
    r"\besta\s+mañana\b", r"\besta\s+tarde\b",
    r"\beste\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b",
    r"\bhoras\s+atrás\b", r"\bminutos\s+atrás\b",
    r"\ben\s+las\s+últimas\s+horas\b",
]


def detect_uncertainty(text: str, title: str = "") -> RuleResult:

    result = RuleResult()
    t = text.lower()
    title_lower = title.lower() if title else ""

    uncertainty_score = 0.0

    # ======================================================
    # CASO 1 — NÚMEROS SIN FUENTE
    # ======================================================

    has_numbers = any(re.search(p, t) for p in NUMBER_PATTERNS)
    has_source  = any(re.search(p, t) for p in SOURCE_INDICATORS)

    if has_numbers and not has_source:
        uncertainty_score += 0.25
        result.reasons.append("numbers_without_source")
        result.evidence.append("Afirmaciones numéricas sin fuente explícita")

    # ======================================================
    # CASO 2 — VERBOS CONDICIONALES COMO HECHOS
    # ======================================================

    conditional_matches = [p for p in CONDITIONAL_PATTERNS if re.search(p, t)]

    if len(conditional_matches) >= 2:
        uncertainty_score += 0.20
        result.reasons.append("conditional_as_fact")
        result.evidence.append(
            f"Verbos condicionales usados como hechos ({len(conditional_matches)})"
        )
    elif len(conditional_matches) == 1:
        uncertainty_score += 0.10
        result.reasons.append("conditional_language")
        result.evidence.append("Lenguaje condicional detectado")

    # ======================================================
    # CASO 3 — AFIRMACIONES CATEGÓRICAS SIN RESPALDO
    # ======================================================

    categorical_matches = [p for p in CATEGORICAL_UNVERIFIED if re.search(p, t)]

    if categorical_matches and not has_source:
        uncertainty_score += 0.20
        result.reasons.append("unverified_categorical_claim")
        result.evidence.append(
            f"Afirmación categórica sin respaldo: {', '.join(categorical_matches[:2])}"
        )

    # ======================================================
    # CASO 4 — HECHO RECIENTE SIN ATRIBUCIÓN
    # ======================================================

    recency_matches = [p for p in RECENCY_PATTERNS if re.search(p, t)]
    has_strong_claim = bool(categorical_matches) or (has_numbers and not has_source)

    if recency_matches and has_strong_claim:
        uncertainty_score += 0.15
        result.reasons.append("recent_unattributed_claim")
        result.evidence.append("Afirmación sobre hecho reciente sin atribución clara")

    # ======================================================
    # CASO 5 — GAP TÍTULO VS CUERPO
    # ======================================================

    if title_lower:
        title_has_strong = any(
            re.search(p, title_lower)
            for p in CATEGORICAL_UNVERIFIED + NUMBER_PATTERNS
        )
        body_sustains = has_source or (
            sum(1 for p in SOURCE_INDICATORS if re.search(p, t)) >= 2
        )

        if title_has_strong and not body_sustains:
            uncertainty_score += 0.20
            result.reasons.append("title_body_gap")
            result.evidence.append(
                "Titular con afirmación fuerte no respaldada en el cuerpo"
            )

    # ======================================================
    # CAP EN 0.45
    # Este módulo nunca lleva a rojo solo.
    # Función: empujar a amarillo estructural.
    # ======================================================

    result.points = round(min(uncertainty_score, 0.45), 3)
    result.reasons = list(dict.fromkeys(result.reasons))
    result.evidence = list(dict.fromkeys(result.evidence))

    return result


def analyze(text: str, title: str = "") -> RuleResult:
    return detect_uncertainty(text, title)