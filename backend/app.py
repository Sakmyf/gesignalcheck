print("VERSION EXTENSION-ID ACTIVA")

import re
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------
# FastAPI Init
# ---------------------------------------
app = FastAPI(title="GE SignalCheck API v3 - Extension Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# EXTENSIONES AUTORIZADAS
# ---------------------------------------
ALLOWED_EXTENSIONS = [
    "fijnjbaacmpnhaaconoafbmnholbmaig"
]

# ---------------------------------------
# Modelo de entrada
# ---------------------------------------
class VerifyRequest(BaseModel):
    url: str
    text: str = ""

# ---------------------------------------
# Score estructural
# ---------------------------------------
def structural_score(url: str, text: str):

    score = 0.5
    signals = []

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if parsed.scheme == "https":
        score += 0.15
        signals.append("HTTPS")

    if domain.endswith(".gov.ar") or domain.endswith(".gob.ar"):
        score += 0.25
        signals.append("Dominio oficial")

    if "vatican.va" in domain:
        score += 0.25
        signals.append("Organismo oficial")

    if "iprofesional.com" in domain:
        score += 0.05
        signals.append("Medio tradicional")

    if len(text.strip()) < 200:
        score -= 0.10
        signals.append("Contenido limitado")

    score = max(0.0, min(score, 1.0))
    return score, signals

# ---------------------------------------
# Score retórico
# ---------------------------------------
def rhetorical_score(text: str):

    score = 0.0
    signals = []

    upper = text.upper()

    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", upper):
        score += 0.3
        signals.append("Lenguaje alarmista")

    if re.search(r"\bCAOS\b|\bCOLAPSO\b|\bTRAICIÓN\b", upper):
        score += 0.2
        signals.append("Carga emocional fuerte")

    if len(re.findall(r"[A-Z]{5,}", text)) > 3:
        score += 0.1
        signals.append("Uso excesivo de mayúsculas")

    return min(score, 1.0), signals

# ---------------------------------------
# Root
# ---------------------------------------
@app.get("/")
def root():
    return {"status": "GE SignalCheck API online"}

# ---------------------------------------
# Endpoint principal
# ---------------------------------------
@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    # 🔐 Validación por ID de extensión
    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension_id = extension_id.strip()

    if extension_id not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    # 1️⃣ Score estructural
    s_score, s_signals = structural_score(data.url, data.text)

    # 2️⃣ Score retórico
    r_score, r_signals = rhetorical_score(data.text)

    # 3️⃣ Índice final
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
