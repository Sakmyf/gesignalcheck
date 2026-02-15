import os
import re
import json
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------
# OpenAI opcional (solo PRO/ENTERPRISE)
# ---------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------
# API Keys por plan
# ---------------------------------------

def parse_keys(env_name: str):
    raw = os.getenv(env_name, "")
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


BASIC_KEYS = parse_keys("API_KEYS_BASIC")
PRO_KEYS = parse_keys("API_KEYS_PRO")
ENTERPRISE_KEYS = parse_keys("API_KEYS_ENTERPRISE")

# Fallback por si alguien usa CLIENT_API_KEY
CLIENT_SINGLE_KEY = os.getenv("CLIENT_API_KEY")
if CLIENT_SINGLE_KEY:
    BASIC_KEYS.append(CLIENT_SINGLE_KEY.strip())


def get_plan(api_key: str):
    if not api_key:
        return None

    api_key = api_key.strip()

    if api_key in ENTERPRISE_KEYS:
        return "enterprise"
    if api_key in PRO_KEYS:
        return "pro"
    if api_key in BASIC_KEYS:
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

    upper = text.upper()

    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", upper):
        score += 0.3
        signals.append("Lenguaje alarmista")

    if re.search(r"\bTRAICIÓN\b|\bCOLAPSO\b|\bCAOS\b", upper):
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
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "IA desactivada"
        }

    if not text or len(text.strip()) < 300:
        return {
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "Texto insuficiente"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=250,
            messages=[
                {
                    "role": "system",
                    "content": "Analiza manipulación discursiva. Devuelve SOLO JSON válido."
                },
                {
                    "role": "user",
                    "content": f"""
Devuelve únicamente:

{{
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
            "manipulative_intent": 0.0,
            "signals": [],
            "status": "Error IA"
        }

# ---------------------------------------
# ENDPOINT PRINCIPAL
# ---------------------------------------
from fastapi import Request, HTTPException

@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    # 🔐 Leer API key (case insensitive)
    incoming_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")

    if not incoming_key:
        raise HTTPException(status_code=401, detail="API key requerida")

    incoming_key = incoming_key.strip()

    plan = get_plan(incoming_key)

    if not plan:
        raise HTTPException(status_code=403, detail="API key inválida")

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente para análisis")

    # 1️⃣ Score estructural
    s_score, s_signals = structural_score(data.url, data.text)

    # 2️⃣ Score retórico heurístico
    r_score_h, r_signals_h = rhetorical_score(data.text)

    # 3️⃣ Score retórico IA (solo si plan lo permite)
    r_score_ai = 0.0
    r_signals_ai = []
    ai_status = "IA no incluida en plan"

    if plan in ["pro", "enterprise"]:
        ai_result = ai_enterprise_analysis(data.text)
        r_score_ai = ai_result.get("manipulative_intent", 0.0)
        r_signals_ai = ai_result.get("signals", [])
        ai_status = ai_result.get("status", "Desconocido")

    # 4️⃣ Combinación retórica
    final_rhetorical = (r_score_h * 0.6) + (r_score_ai * 0.4)

    # 5️⃣ Índice final
    risk_index = (final_rhetorical * 0.8) + ((1 - s_score) * 0.2)

    # Anti falsos positivos
    if final_rhetorical < 0.15:
        risk_index = min(risk_index, 0.45)

    risk_index = max(0.0, min(risk_index, 1.0))

    return {
        "plan": plan,
        "structural_trust_score": round(s_score, 2),
        "rhetorical_manipulation_score": round(final_rhetorical, 2),
        "risk_index": round(risk_index, 2),
        "details": {
            "structural_signals": s_signals,
            "rhetorical_signals": list(set(r_signals_h + r_signals_ai)),
            "ai_status": ai_status
        }
    }
