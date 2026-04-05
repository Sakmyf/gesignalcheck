# ======================================================
# SIGNALCHECK BACKEND – STABLE + CONTEXT FIX
# ======================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time

# =========================
# IMPORTS DEL MOTOR
# =========================
from backend.engine import analyze_content

app = FastAPI()

# =========================
# CORS (PRODUCCIÓN SIMPLE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # después lo cerramos si querés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELO REQUEST
# =========================
class AnalyzeRequest(BaseModel):
    url: str
    content: str

# =========================
# UTIL: HASH DETERMINÍSTICO
# =========================
def generate_analysis_key(url: str, content: str) -> str:
    raw = f"{url}|{hashlib.sha256(content.encode()).hexdigest()}|v13"
    return hashlib.sha256(raw.encode()).hexdigest()

# =========================
# CONTEXT OVERRIDE (CLAVE)
# =========================
def apply_context_override(score: float, url: str) -> float:

    url = url.lower()

    institutional_domains = [
        "gob.ar",
        "argentina.gob.ar",
        "indec.gob.ar",
        "casa rosada",
        "usa.gov",
        "gov",
        "edu"
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
# MAPEO SCORE → NIVEL
# =========================
def get_level(score: float) -> str:
    if score < 0.3:
        return "bajo"
    elif score < 0.6:
        return "moderado"
    else:
        return "alto"

# =========================
# MENSAJE UX
# =========================
def get_message(score: float) -> str:

    if score < 0.3:
        return "El contenido no presenta señales relevantes de manipulación o riesgo."

    elif score < 0.6:
        return "Se detectan ciertos patrones que requieren una lectura más atenta."

    else:
        return "Se detectan múltiples señales asociadas a contenido potencialmente problemático."

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
    # MOTOR BASE
    # =========================
    base_result = analyze_content(data.content)

    score = base_result.get("score", 0.0)
    confidence = base_result.get("confidence", 0.5)

    # =========================
    # 🔥 CONTEXT FIX
    # =========================
    score = apply_context_override(score, data.url)

    # Clamp final (seguridad)
    score = max(0.0, min(score, 1.0))

    # =========================
    # OUTPUT
    # =========================
    level = get_level(score)
    message = get_message(score)

    return {
        "analysis_key": analysis_key,
        "url": data.url,
        "score": round(score * 100),
        "level": level,
        "confidence": round(confidence * 100),
        "message": message,
        "timestamp": int(time.time()),
        "engine_version": "v13-context-fix"
    }

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"status": "SignalCheck backend operativo"}