import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
from urllib.parse import urlparse

app = FastAPI()

# --- CORS (IMPORTANTE para que la extensión pueda llamar al backend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelo de entrada ---
class VerifyRequest(BaseModel):
    url: str
    text: str = ""
    page_type: str = "unknown"


# --- Función de análisis simple (puede crecer después) ---
def analyze_content(url: str, text: str):

    score = 0.5  # base neutra
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

    # Vaticano / organismos oficiales
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

    # Limitar score entre 0 y 1
    score = max(0.0, min(score, 1.0))

    return score, signals


# --- Clasificación correcta ---
def classify(score: float):

    if score >= 0.75:
        return "Alta confiabilidad"
    elif score >= 0.45:
        return "En debate"
    else:
        return "Riesgo alto"


# --- Endpoint raíz ---
@app.get("/")
def root():
    return {"status": "Candado API online"}


# --- Endpoint principal ---
@app.post("/v1/verify")
def verify(data: VerifyRequest):

    score, signals = analyze_content(data.url, data.text)
    label = classify(score)

    return {
        "score": round(score, 2),
        "label": label,
        "signals": signals
    }
