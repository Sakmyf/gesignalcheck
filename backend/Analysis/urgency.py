import re
from backend.Analysis.rules_types import RuleResult

# 🔥 FIX: Combinamos palabras sueltas de alta presión con frases hechas
URGENCY_KEYWORDS = [
    r"urgente", r"ahora", r"ya", r"inmediato", r"rápido", 
    r"oferta", r"promoción", r"descuento", r"oportunidad", r"gane"
]

URGENCY_PATTERNS = [
    r"última oportunidad",
    r"actu[aá] ahora",
    r"antes (de )?que lo borren",
    r"solo\s+por\s+hoy",
    r"tiempo\s+limitado",
    r"decisión\s+inmediata" 
]

def check_urgency(text: str) -> RuleResult:
    result = RuleResult()
    text_lower = text.lower()
    matches = 0

    # 1. Buscar frases completas (valen más puntos)
    for pattern in URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            matches += 2 # Suma doble

    # 2. Buscar palabras sueltas
    for word in URGENCY_KEYWORDS:
        if word in text_lower:
            matches += 1

    if matches >= 1:
        # Escalamos el score para que se note en la extensión
        score = min(0.9, matches * 0.15)
        result.points += score
        result.reasons.append("urgency_pressure")
        result.evidence.append(f"Señales de urgencia detectadas: {matches}")

    return result

def analyze(text: str):
    return check_urgency(text)