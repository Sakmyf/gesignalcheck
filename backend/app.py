print("VERSION EXTENSION-ID ACTIVA")

import re
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------
# FastAPI Init
# ---------------------------------------
app = FastAPI(title="GE SignalCheck API v4 - Extension Mode")

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
# Score estructural V4
# ---------------------------------------
def structural_score(url: str, text: str):

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    signals = []
    domain_type = "unknown"

    INSTITUTIONAL = [".gov", ".gov.ar", ".gob.ar", ".edu", ".edu.ar"]
    TRADITIONAL_MEDIA = ["reuters.com", "bbc.com", "lanacion.com.ar", "clarin.com"]
    SOCIAL_MEDIA = ["facebook.com", "twitter.com", "x.com", "instagram.com", "tiktok.com"]
    SHORTENERS = ["bit.ly", "tinyurl.com"]

    # Base trust por defecto
    trust = 0.45

    if any(domain.endswith(tld) for tld in INSTITUTIONAL):
        trust = 0.85
        domain_type = "institutional"
        signals.append("Dominio institucional")

    elif any(media in domain for media in TRADITIONAL_MEDIA):
        trust = 0.70
        domain_type = "traditional_media"
        signals.append("Medio tradicional")

    elif any(social in domain for social in SOCIAL_MEDIA):
        trust = 0.35
        domain_type = "social"
        signals.append("Contenido en red social")

    elif any(short in domain for short in SHORTENERS):
        trust = 0.25
        domain_type = "shortener"
        signals.append("Dominio acortador")

    if parsed.scheme == "https":
        trust += 0.05
        signals.append("HTTPS")

    if len(text.strip()) < 200:
        trust -= 0.05
        signals.append("Contenido limitado")

    trust = max(0.0, min(trust, 1.0))

    return trust, signals, domain_type

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
    trust_score, s_signals, domain_type = structural_score(data.url, data.text)

    # 2️⃣ Score retórico
    r_score, r_signals = rhetorical_score(data.text)

    # 3️⃣ Índice final
    risk_index = (r_score * 0.7) + ((1 - trust_score) * 0.3)

    # Piso mínimo para redes sociales
    if domain_type == "social":
        risk_index = max(risk_index, 0.30)

    risk_index = max(0.0, min(risk_index, 1.0))

    return {
        "structural_trust_score": round(trust_score, 2),
        "source_type": domain_type,
        "rhetorical_manipulation_score": round(r_score, 2),
        "risk_index": round(risk_index, 2),
        "details": {
            "structural_signals": s_signals,
            "rhetorical_signals": r_signals
        }
    }
