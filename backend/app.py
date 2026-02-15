import os
import re
import json
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------
# OpenAI opcional
# ---------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------
# API Keys por plan
# ---------------------------------------
BASIC_KEYS = [k.strip() for k in os.getenv("API_KEYS_BASIC", "").split(",") if k.strip()]
PRO_KEYS = [k.strip() for k in os.getenv("API_KEYS_PRO", "").split(",") if k.strip()]
ENTERPRISE_KEYS = [k.strip() for k in os.getenv("API_KEYS_ENTERPRISE", "").split(",") if k.strip()]

def get_plan(api_key: str):
    if api_key in ENTERPRISE_KEYS:
        return "enterprise"
    elif api_key in PRO_KEYS:
        return "pro"
    elif api_key in BASIC_KEYS:
        return "basic"
    return None

# ---------------------------------------
# FastAPI Init
# ---------------------------------------
app = FastAPI(title="GESignalCheck B2B API v3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# Modelo entrada
# ---------------------------------------
class VerifyRequest(BaseModel):
    url: str
    text: str = ""

# ---------------------------------------
# Listas estructurales
# ---------------------------------------
TRUSTED_TLDS = [".gov", ".gov.ar", ".gob.ar", ".edu", ".edu.ar", ".org"]

TRADITIONAL_MEDIA = [
    "iprofesional.com",
    "lanacion.com.ar",
    "clarin.com",
    "reuters.com",
    "bbc.com"
]

# ---------------------------------------
# SCORE ESTRUCTURAL
# ---------------------------------------
def structural_score(url: str, text: str):

    score = 0.5
    signals = []

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if parsed.scheme == "https":
        score += 0.10
        signals.append("HTTPS")

    if any(domain.endswith(tld) for tld in TRUSTED_TLDS):
        score += 0.25
        signals.append("Dominio institucional")

    if any(media in domain for media in TRADITIONAL_MEDIA):
        score += 0.10
        signals.append("Medio tradicional")

    if len(text.strip()) < 200:
        score -= 0.10
        signals.append("Contenido limitado")

    score = max(0.0, min(score, 1.0))
    return score, signals

# ---------------------------------------
# SCORE RETÓRICO HEURÍSTICO
# ---------------------------------------
def rhetorical_score(text: str):

    score = 0.0
    signals = []

    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", text.upper()):
        score += 0.3
        signals.append("Lenguaje alarmista")

    if re.search(r"\bTRAICIÓN\b|\bCOLAPSO\b|\bCAOS\b", text.upper()):
        score += 0.2
        signals.append("Carga emocional fuerte")

    if len(re.findall(r"[A-Z]{5,}", text)) > 3:
        score += 0.1
        signals.append("Uso excesivo de mayúsculas")

    return min(score, 1.0), signals

# ---------------------------------------
# IA ENTERPRISE
# ---------------------------------------
def ai_enterprise_analysis(text: str):

    if not client:
        return {
            "emotional_intensity": 0.0,
            "alarmism": 0.0,
            "polarization": 0.0,
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "IA desactivada"
        }

    if not text or len(text.strip()) < 300:
        return {
            "emotional_intensity": 0.0,
            "alarmism": 0.0,
            "polarization": 0.0,
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "Texto insuficiente"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": """
Analiza patrones discursivos.
NO evalúes ideología ni religión.
Evalúa intención manipulativa y estructura retórica.
Devuelve SOLO JSON válido.
"""
                },
                {
                    "role": "user",
                    "content": f"""
Devuelve únicamente:

{{
  "emotional_intensity": 0.0,
  "alarmism": 0.0,
  "polarization": 0.0,
  "manipulative_intent": 0.0,
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

        parsed["status"] = "IA activa"
        return parsed

    except Exception as e:
        print("AI error:", e)
        return {
            "emotional_intensity": 0.0,
            "alarmism": 0.0,
            "polarization": 0.0,
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "Error IA"
        }

# ---------------------------------------
# ROOT
# ---------------------------------------
@app.get("/")
def root():
    return {"status": "GESignalCheck B2B API v3 online"}

# ---------------------------------------
# ENDPOINT PRINCIPAL
# ---------------------------------------
@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key requerida")

    plan = get_plan(api_key)
    if not plan:
        raise HTTPException(status_code=403, detail="API key inválida")

    # 1️⃣ Score estructural
    s_score, s_signals = structural_score(data.url, data.text)

    # 2️⃣ Heurístico retórico
    r_score_h, r_signals_h = rhetorical_score(data.text)

    # 3️⃣ IA enterprise
    ai_data = ai_enterprise_analysis(data.text)

    # 4️⃣ Score retórico enterprise ponderado
    final_rhetorical = (
        ai_data["manipulative_intent"] * 0.40 +
        ai_data["alarmism"] * 0.20 +
        ai_data["polarization"] * 0.20 +
        ai_data["emotional_intensity"] * 0.20
    )

    # 5️⃣ Índice final de riesgo
    risk_index = (1 - s_score) * 0.5 + final_rhetorical * 0.5

    # -----------------------------------
    # RESPUESTAS SEGÚN PLAN
    # -----------------------------------

    if plan == "basic":
        return {
            "risk_index": round(risk_index, 2)
        }

    if plan == "pro":
        return {
            "structural_score": round(s_score, 2),
            "rhetorical_score": round(final_rhetorical, 2),
            "risk_index": round(risk_index, 2)
        }

    if plan == "enterprise":
        return {
            "structural_trust_score": round(s_score, 2),
            "emotional_intensity": ai_data["emotional_intensity"],
            "alarmism": ai_data["alarmism"],
            "polarization": ai_data["polarization"],
            "manipulative_intent": ai_data["manipulative_intent"],
            "risk_index": round(risk_index, 2),
            "signals": list(set(s_signals + r_signals_h + ai_data["signals"])),
            "engine_version": "B2B-v3",
            "ai_status": ai_data["status"]
        }
