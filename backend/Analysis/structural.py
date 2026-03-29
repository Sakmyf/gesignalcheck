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
    text_length = len(text)

    # ======================================================
    # 1. 🔴 Generalizaciones absolutas (Lógica Proporcional)
    # ======================================================
    absolute_count = sum(len(re.findall(p, text_lower)) for p in ABSOLUTES)
    
    # Calculamos cuántos "miles de caracteres" tiene el texto
    text_length_k = max(1.0, text_length / 1000.0)
    
    # Permitimos ~4 términos absolutos por cada 1,000 caracteres
    allowed_absolutes = int(text_length_k * 4)

    if absolute_count > allowed_absolutes:
        # Solo penalizamos el EXCESO
        excess = absolute_count - allowed_absolutes
        score_addition = min(0.8, excess * 0.1) # Tope máximo de 0.8
        
        result.points += score_addition
        result.reasons.append("absolute_generalization")
        result.evidence.append(
            f"Uso desproporcionado de generalizaciones (encontradas {absolute_count}, esperado max {allowed_absolutes})"
        )

    # ======================================================
    # 2. 🟠 Clickbait estructural (Ajuste Escalonado)
    # ======================================================
    clickbait_matches = [p for p in CLICKBAIT_PATTERNS if re.search(p, text_lower)]
    
    if clickbait_matches:
        # En lugar de sumar 0.7 de golpe, sumamos 0.2 por cada patrón encontrado
        score_addition = min(0.7, len(clickbait_matches) * 0.2)
        
        result.points += score_addition
        result.reasons.append("clickbait_structure")
        result.evidence.append(f"Patrones clickbait detectados: {', '.join(clickbait_matches)}")

    # ======================================================
    # 3. 🟡 Exceso de mayúsculas (Mantiene su lógica de ratio)
    # ======================================================
    uppercase_ratio = sum(1 for c in text if c.isupper()) / max(text_length, 1)

    if uppercase_ratio > 0.25 and text_length > 30:
        result.points += 0.6
        result.reasons.append("excessive_uppercase")
        result.evidence.append(f"Uso excesivo de mayúsculas ({int(uppercase_ratio * 100)}%)")

    return result


def analyze(text: str):
    return check_structural(text)