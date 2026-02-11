import os
import re
import json
from urllib.parse import urlparse

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI


# ----------------------------
# OpenAI Client
# ----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ----------------------------
# FastAPI Init
# ----------------------------
app = FastAPI()


# ----------------------------
# CORS (IMPORTANTE para la extensión)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Modelo de entrada
# ----------------------------
class VerifyRequest(BaseModel):
    url: str
    text: str = ""
    page_type: str = "unknown"


# ----------------------------
# Motor heurístico (gratis y rápido)
# ----------------------------
def analyze_heuristic(url: str, text: str):

    score = 0.5
    signals = []

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # HTTPS
    if parsed.scheme == "https":
        score += 0.15
        signals.append("HTTPS")

    # Dominios oficiales argentinos
    if domain.endswith(".gov.ar"):
        score += 0.25
        signals.append("Identidad verificable")

    # Organismos oficiales
    if "vatican.va" in domain:
        score += 0.25
        signals.append("Organismo oficial")

    # Medios tradicionales
    if "iprofesional.com" in domain:
        score += 0.05
        signals.append("Medio tradicional")

    # Lenguaje alarmista
    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", text.upper()):
        score -= 0.2
        signals.append("Lenguaje alarmista")

    score = max(0.0, min(score, 1.0))

    return score, signals


# ----------------------------
# Motor IA (contextual)
# ----------------------------
def analyze_ai(text: str):

    # Si el texto es muy corto, no llamamos IA (ahorra dinero)
    if not text or len(text.strip()) < 100:
        return 0.5, []

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=200,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analizador técnico de señales discursivas. Responde SOLO JSON válido."
                },
                {
                    "role": "user",
                    "content": f"""
Analiza el siguiente texto y detecta señales de manipulación emocional o retórica alarmista.

Devuelve SOLO este formato JSON:

{{
  "score": 0.0,
  "signals": ["string"]
}}

Texto:
{text[:3000]}
"""
                }
            ]
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        return parsed.get("score", 0.5), parsed.get("signals", [])

    except Exception as e:
        print("AI error:", e)
        return 0.5, []


# ----------------------------
# Clasificación final
# ----------------------------
def classify(score: float):

    if score >= 0.75:
        return "Alta confiabilidad"
    elif score >= 0.45:
        return "En debate"
    else:
        return "Riesgo alto"


# ----------------------------
# Endpoint raíz
# ----------------------------
@app.get("/")
def root():
    return {"status": "GESignalCheck API online"}
# ----------------------------
# Endpoint principal
# ----------------------------
@app.post("/v1/verify")
def verify(data: VerifyRequest):

    # 1️⃣ Reglas locales
    h_score, h_signals = analyze_heuristic(data.url, data.text)

    # 2️⃣ IA contextual
    ai_score, ai_signals = analyze_ai(data.text)

    # 3️⃣ Modelo híbrido ponderado
    final_score = (h_score * 0.6) + (ai_score * 0.4)

    label = classify(final_score)

    return {
        "score": round(final_score, 2),
        "label": label,
        "signals": list(set(h_signals + ai_signals))
    }
