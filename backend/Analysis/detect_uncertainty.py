# ======================================================
# SIGNALCHECK — UNCERTAINTY ENGINE v2.0 (CONTEXT-AWARE)
# ======================================================

import re
from backend.Analysis.rules_types import RuleResult


# ======================================================
# PATTERNS
# ======================================================

NUMBER_PATTERNS = [
    r"\b\d+[\.,]?\d*\s*(mil|millones?|billones?|personas?|empleos?|puestos?|casos?|muertes?|contagios?)\b",
    r"\b\d+\s*%",
    r"\b\d+\s*de\s*cada\s*\d+\b",
]

STRONG_SOURCES = [
    r"\bindec\b", r"\bcepal\b", r"\boms\b", r"\bministerio\b",
    r"\bgobierno\b", r"\boficial\b", r"\bestadística\b",
]

WEAK_SOURCES = [
    r"\bestudio\b", r"\binforme\b", r"\bdatos\b",
    r"\bsegún\b", r"\bfuentes\b",
]

CONDITIONAL_PATTERNS = [
    r"\bhabría\b", r"\bhabrían\b",
    r"\bsería\b", r"\bserían\b",
    r"\bestaría\b", r"\bestarían\b",
    r"\bpodría\b", r"\bpodrían\b",
    r"\bdebería\b", r"\bdeberían\b",
    r"\btrascendió\b", r"\bse supo\b",
    r"\bse conoció\b", r"\bse especula\b",
]

CATEGORICAL_UNVERIFIED = [
    r"\bes el peor\b", r"\bes el mejor\b",
    r"\bnunca antes\b", r"\bjamás\b",
    r"\bhistórico\b", r"\bsin precedentes\b",
    r"\bla mayor\b", r"\bla menor\b",
    r"\bcompletamente\b", r"\btotalmente\b",
]

RECENCY_PATTERNS = [
    r"\bhoy\b", r"\bayer\b", r"\banoche\b",
    r"\besta\s+mañana\b", r"\besta\s+tarde\b",
    r"\bhoras\s+atrás\b", r"\bminutos\s+atrás\b",
]


# ======================================================
# MAIN FUNCTION
# ======================================================

def detect_uncertainty(text: str, title: str = "", context: str = "general") -> RuleResult:

    result = RuleResult()

    t = text.lower()
    title_lower = title.lower() if title else ""

    # ======================================================
    # CONTEXT FILTER
    # ======================================================

    if context in ["ecommerce", "product", "landing"]:
        return result  # no aplica

    if context in ["government", "institutional"]:
        context_multiplier = 0.3
    elif context == "news":
        context_multiplier = 1.0
    else:
        context_multiplier = 0.6

    uncertainty_score = 0.0

    # ======================================================
    # SOURCE DETECTION
    # ======================================================

    has_strong_source = any(re.search(p, t) for p in STRONG_SOURCES)
    has_weak_source = any(re.search(p, t) for p in WEAK_SOURCES)

    # ======================================================
    # CASE 1 — NUMBERS WITHOUT SOURCE
    # ======================================================

    has_numbers = any(re.search(p, t) for p in NUMBER_PATTERNS)

    if has_numbers and not has_strong_source:
        if has_weak_source:
            uncertainty_score += 0.10
        else:
            uncertainty_score += 0.25

        result.reasons.append("numbers_without_strong_source")
        result.evidence.append("Datos numéricos sin fuente sólida")

    # ======================================================
    # CASE 2 — CONDITIONAL LANGUAGE (EXCESIVO)
    # ======================================================
    # 🔥 FIX: Lógica Proporcional al largo del texto
    
    conditional_count = sum(len(re.findall(p, t)) for p in CONDITIONAL_PATTERNS)
    
    # Calculamos cuántos "miles de caracteres" tiene el texto (min 1)
    text_length_k = max(1.0, len(text) / 1000.0)
    
    # Tolerancia: Es normal usar ~3 condicionales cada 1.000 caracteres en español
    allowed_conditionals = int(text_length_k * 3)

    if conditional_count > allowed_conditionals:
        # Solo penalizamos el EXCESO de condicionales
        excess = conditional_count - allowed_conditionals
        uncertainty_score += min(0.3, excess * 0.05)
        
        result.reasons.append("excessive_conditional_language")
        result.evidence.append(
            f"Uso excesivo de condicionales (encontrados {conditional_count}, esperado max {allowed_conditionals})"
        )

    # ======================================================
    # CASE 3 — CATEGORICAL CLAIM WITHOUT BACKING
    # ======================================================

    categorical_matches = [p for p in CATEGORICAL_UNVERIFIED if re.search(p, t)]

    if categorical_matches and not has_strong_source:
        uncertainty_score += 0.20
        result.reasons.append("unverified_categorical_claim")
        result.evidence.append("Afirmación categórica sin respaldo")

    # ======================================================
    # CASE 4 — RECENT CLAIM WITHOUT ATTRIBUTION
    # ======================================================

    recency_matches = [p for p in RECENCY_PATTERNS if re.search(p, t)]
    has_strong_claim = bool(categorical_matches) or has_numbers

    if recency_matches and has_strong_claim and not has_strong_source:
        uncertainty_score += 0.15
        result.reasons.append("recent_unattributed_claim")
        result.evidence.append("Hecho reciente sin atribución clara")

    # ======================================================
    # CASE 5 — TITLE vs BODY GAP
    # ======================================================

    if title_lower:

        title_strong = any(
            re.search(p, title_lower)
            for p in CATEGORICAL_UNVERIFIED + NUMBER_PATTERNS
        )

        body_supports = has_strong_source or (
            sum(1 for p in WEAK_SOURCES if re.search(p, t)) >= 2
        )

        if title_strong and not body_supports:
            uncertainty_score += 0.20
            result.reasons.append("title_body_gap")
            result.evidence.append("El titular no está respaldado por el contenido")

    # ======================================================
    # FINAL ADJUSTMENT
    # ======================================================

    uncertainty_score *= context_multiplier

    result.points = round(min(uncertainty_score, 0.45), 3)

    result.reasons = list(dict.fromkeys(result.reasons))
    result.evidence = list(dict.fromkeys(result.evidence))

    return result


# ======================================================
# EXPORT
# ======================================================

def analyze(text: str, title: str = "", context: str = "general") -> RuleResult:
    return detect_uncertainty(text, title, context)