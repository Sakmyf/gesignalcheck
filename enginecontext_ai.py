# ======================================================
# SIGNALCHECK — CONTEXT AI (READY FOR INTEGRATION)
# ======================================================

def analyze_context_ai(url: str, text: str) -> dict:
    """
    Análisis contextual (IA opcional).
    No determina verdad.
    Evalúa contexto interpretativo.
    """

    if not text:
        return {
            "page_type": "unknown",
            "tone": "neutral",
            "intent": "inform",
            "risk_level": "low",
            "notes": "sin contenido"
        }

    # --------------------------------------------------
    # PROMPT (para uso futuro con LLM)
    # --------------------------------------------------

    prompt = f"""
Actuás como un analista de contexto informativo.

Evaluá:
- tipo de fuente
- tono
- intención
- riesgo interpretativo

URL:
{url}

CONTENIDO:
{text[:3000]}
"""

    # --------------------------------------------------
    # PLACEHOLDER ACTUAL (SIN IA)
    # --------------------------------------------------

    return {
        "page_type": "unknown",
        "tone": "neutral",
        "intent": "inform",
        "risk_level": "medium",
        "notes": "análisis contextual no activado (modo heurístico)"
    }