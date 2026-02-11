# enginecontext_ai.py

def analyze_context(url: str, text: str) -> dict:
    """
    Analiza contexto informativo usando IA.
    NO decide verdad/falsedad.
    SOLO evalúa señales contextuales.
    """

    prompt = f"""
Actuás como un analista de contexto informativo, NO como verificador de hechos.

Objetivo:
Detectar señales de contexto que puedan influir en la interpretación del contenido.

REGLAS ESTRICTAS:
- NO clasifiques como falso contenido legítimo.
- NO penalices medios reconocidos solo por estilo periodístico.
- El rojo solo corresponde a estafas, manipulación o contradicción explícita.
- El amarillo es el estado por defecto si hay duda.
- El verde se usa cuando el contenido es informativo, institucional o neutral.

Evaluá SOLO estas dimensiones:
1. Tipo de fuente (institucional, comercial, periodística, social)
2. Tono (neutral, emocional, alarmista, promocional)
3. Intención aparente (informar, persuadir, vender, asustar)
4. Riesgo de mala interpretación por lector promedio

DEVOLVÉ EXCLUSIVAMENTE ESTE JSON:
{{
  "page_type": "news | ecommerce | institutional | social | unknown",
  "tone": "neutral | emotional | alarmist | promotional",
  "intent": "inform | persuade | sell | warn",
  "risk_level": "low | medium | high",
  "notes": "breve explicación humana"
}}

URL:
{url}

CONTENIDO:
{text[:4000]}
"""

    # ⚠️ placeholder: acá luego conectás OpenAI / LLM real
    return {
        "page_type": "news",
        "tone": "neutral",
        "intent": "inform",
        "risk_level": "low",
        "notes": "Contenido informativo sin señales de manipulación."
    }
