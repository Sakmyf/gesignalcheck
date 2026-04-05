# ======================================================
# SIGNALCHECK BACKEND – STABLE FINAL (ENGINE COMPATIBLE)
# ======================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time

# =========================
# IMPORT DEL ENGINE REAL
# =========================
from backend.engine import analyze  # 🔥 FIX IMPORT

app = FastAPI()

# =========================
# CORS (SIMPLE PROD)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================
class AnalyzeRequest(BaseModel):
    url: str
    content: str

# =========================
# HASH DETERMINÍSTICO
# =========================
def generate_analysis_key(url: str, content: str) -> str:
    raw = f"{url}|{hashlib.sha256(content.encode()).hexdigest()}|v13"
    return hashlib.sha256(raw.encode()).hexdigest()

# =========================
# CONTEXT OVERRIDE
# =========================
def apply_context_override(score: float, url: str) -> float:

    url = url.lower()

    institutional_domains = [
        "gob.ar",
        "argentina.gob.ar",
        "indec.gob.ar",
        "casarosada.gob.ar",
        "usa.gov",
        ".gov",
        ".edu"
    ]

    factcheck_domains = [
        "maldita.es",
        "chequeado.com",
        "factcheck.org"
    ]

    if any(domain in url for domain in institutional_domains):
        return min(score, 0.15)

    if any(domain in url for domain in factcheck_domains):
        return min(score, 0.20)

    return score

# =========================
# SCORE → NIVEL
# =========================
def get_level(score: float) -> str:
    if score < 0.3:
        return "bajo"
    elif score < 0.6:
        return "moderado"
    else:
        return "alto"

# =========================
# MENSAJE UX COHERENTE
# =========================
def get_message(score: float) -> str:

    if score < 0.3:
        return "El contenido no presenta señales relevantes de manipulación o riesgo."

    elif score < 0.6:
        return "Se detectan ciertos patrones que requieren una lectura más atenta."

    else:
        return "Se detectan múltiples señales asociadas a contenido potencialmente problemático."

# =========================
# NORMALIZADOR ENGINE (CLAVE)
# =========================
def normalize_engine_output(result: dict):

    # fallback seguro
    score = result.get("score", 0.0)
    confidence = result.get("confidence", 0.5)

    # por si viene en otro formato
    if score > 1:
        score = score / 100

    if confidence > 1:
        confidence = confidence / 100

    return score, confidence

# =========================
# ENDPOINT PRINCIPAL
# =========================
@app.post("/v3/verify")
async def verify(data: AnalyzeRequest, request: Request):

    if not data.url or not data.content:
        raise HTTPException(status_code=400, detail="Faltan datos")

    # =========================
    # HASH
    # =========================
    analysis_key = generate_analysis_key(data.url, data.content)

    # =========================
    # MOTOR
    # =========================
    base_result = analyze(data.content)

    score, confidence = normalize_engine_output(base_result)

    # =========================
    # 🔥 CONTEXT FIX
    # =========================
    score = apply_context_override(score, data.url)

    # Clamp final
    score = max(0.0, min(score, 1.0))
    confidence = max(0.0, min(confidence, 1.0))

    # =========================
    # OUTPUT
    # =========================
    level = get_level(score)
    message = get_message(score)

    return {
        "analysis_key": analysis_key,
        "url": data.url,
        "score": int(score * 100),
        "level": level,
        "confidence": int(confidence * 100),
        "message": message,
        "timestamp": int(time.time()),
        "engine_version": "v13-context-stable"
    }

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"status": "SignalCheck backend operativo"}