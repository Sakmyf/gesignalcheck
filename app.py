print("VERSION NUEVA ACTIVA")

import os
import re
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ---------------------------------------
# EXTENSIONES AUTORIZADAS
# ---------------------------------------
ALLOWED_EXTENSIONS = [
    "fijnjbaacmpnhaaconoafbmnholbmaig"
]

# ---------------------------------------
# CORS
# ---------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# API KEYS
# ----------------------------

BASIC_KEYS = [
    k.strip()
    for k in os.getenv("API_KEYS_BASIC", "").split(",")
    if k.strip()
]

PRO_KEYS = [
    k.strip()
    for k in os.getenv("API_KEYS_PRO", "").split(",")
    if k.strip()
]

ENTERPRISE_KEYS = [
    k.strip()
    for k in os.getenv("API_KEYS_ENTERPRISE", "").split(",")
    if k.strip()
]


def get_plan(api_key: str):
    if api_key in ENTERPRISE_KEYS:
        return "enterprise"
    if api_key in PRO_KEYS:
        return "pro"
    if api_key in BASIC_KEYS:
        return "basic"
    return None

# ----------------------------
# Modelo
# ----------------------------
class VerifyRequest(BaseModel):
    url: str
    text: str = ""


# ----------------------------
# Score estructural
# ----------------------------
def structural_score(url: str, text: str):
    score = 0.5
    signals = []

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if parsed.scheme == "https":
        score += 0.15
        signals.append("HTTPS")

    if domain.endswith(".gov.ar"):
        score += 0.25
        signals.append("Dominio oficial")

    if "vatican.va" in domain:
        score += 0.25
        signals.append("Organismo oficial")

    if "iprofesional.com" in domain:
        score += 0.05
        signals.append("Medio tradicional")

    score = max(0.0, min(score, 1.0))
    return score, signals


# ----------------------------
# Score retórico simple
# ----------------------------
def rhetorical_score(text: str):
    score = 0.0
    signals = []

    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", text.upper()):
        score += 0.3
        signals.append("Lenguaje alarmista")

    if re.search(r"\bCAOS\b|\bCOLAPSO\b|\bTRAICIÓN\b", text.upper()):
        score += 0.2
        signals.append("Carga emocional fuerte")

    return min(score, 1.0), signals


# ----------------------------
# Root
# ----------------------------
@app.get("/")
def root():
    return {"status": "GE Signal Check API online"}


# ----------------------------
# Endpoint principal
# ----------------------------
@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    print(">>> VERSION EXTENSION-ID ACTIVA <<<")

    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension_id = extension_id.strip()

    if extension_id not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    s_score, s_signals = structural_score(data.url, data.text)
    r_score, r_signals = rhetorical_score(data.text)

    risk_index = (r_score * 0.7) + ((1 - s_score) * 0.3)
    risk_index = max(0.0, min(risk_index, 1.0))

    return {
        "structural_trust_score": round(s_score, 2),
        "rhetorical_manipulation_score": round(r_score, 2),
        "risk_index": round(risk_index, 2),
        "details": {
            "structural_signals": s_signals,
            "rhetorical_signals": r_signals
        }
    }