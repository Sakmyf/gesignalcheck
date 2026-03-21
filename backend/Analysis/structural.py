import re
from backend.Analysis.rules_types import RuleResult


ABSOLUTES = [
    r"\btodos\b",
    r"\bnadie\b",
    r"\bsiempre\b",
    r"\bnunca\b",
]

CLICKBAIT_PATTERNS = [
    r"no vas a creer",
    r"lo que pasó después",
    r"te sorprenderá",
    r"impactante",
    r"increíble",
]


def check_structural(text: str) -> RuleResult:

    result = RuleResult()
    text_lower = text.lower()

    # 🔴 Generalizaciones absolutas repetidas
    absolute_count = sum(len(re.findall(p, text_lower)) for p in ABSOLUTES)

    if absolute_count >= 2:
        result.points += 0.8
        result.reasons.append("absolute_generalization")
        result.evidence.append(
            f"Generalizaciones absolutas detectadas ({absolute_count})"
        )

    # 🟠 Clickbait estructural
    for p in CLICKBAIT_PATTERNS:
        if re.search(p, text_lower):
            result.points += 0.7
            result.reasons.append("clickbait_structure")
            result.evidence.append(f"Patrón clickbait detectado: {p}")

    # 🟡 Exceso de mayúsculas
    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

    if uppercase_ratio > 0.25 and len(text) > 30:
        result.points += 0.6
        result.reasons.append("excessive_uppercase")
        result.evidence.append("Uso excesivo de mayúsculas")

    # 🟡 Exclamaciones múltiples
    if text.count("!") >= 3:
        result.points += 0.5
        result.reasons.append("excessive_exclamations")
        result.evidence.append("Uso reiterado de exclamaciones")

    return result


def analyze(text: str):
    return check_structural(text)