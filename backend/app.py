# ======================================================
# SIGNALCHECK API – APP.PY (ESTABLE + FIX SCORE + UX)
# ======================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time

# 🔥 IMPORT ENGINE (ajustalo a tu path real si cambia)
from backend.engine import analyze_text

app = FastAPI()

# ======================================================
# 🌐 CORS (AJUSTAR EN PRODUCCIÓN)
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 luego limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 📦 REQUEST MODEL
# ======================================================

class VerifyRequest(BaseModel):
    url: str
    text: str


# ======================================================
# 🔐 HELPERS
# ======================================================

def generate_analysis_key(url: str, text: str) -> str:
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    base = f"{url}|{content_hash}|v13"
    return hashlib.sha256(base.encode()).hexdigest()


def calculate_level(score_norm: float) -> str:
    if score_norm >= 0.7:
        return "alto"
    elif score_norm >= 0.3:
        return "moderado"
    else:
        return "bajo"


def build_message(level: str) -> str:
    if level == "alto":
        return "Se detectan múltiples señales de riesgo estructural."
    elif level == "moderado":
        return "Señales mixtas — lectura crítica recomendada."
    else:
        return "Bajo riesgo estructural detectado."


def calculate_confidence(result: dict) -> int:
    # 🔥 heurística simple (después la refinamos)
    signals = len(result.get("reasons", []))
    base = 30 + signals * 10
    return max(10, min(base, 95))


# ======================================================
# 🚀 ENDPOINT PRINCIPAL
# ======================================================

@app.post("/v3/verify")
async def verify(req: VerifyRequest, request: Request):

    # 🔐 HEADER VALIDATION
    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no autorizada")

    # 🧠 GENERAR KEY DETERMINÍSTICA
    analysis_key = generate_analysis_key(req.url, req.text)

    # ==================================================
    # 🧠 ENGINE
    # ==================================================

    try:
        result = analyze_text(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    raw_score = result.get("score", 0)

    # ==================================================
    # 🔥 FIX DE ESCALA (CLAVE)
    # ==================================================

    if raw_score <= 5:
        score_norm = raw_score / 20
    else:
        score_norm = raw_score / 100

    score_norm = max(0, min(score_norm, 1))

    # ==================================================
    # 🎯 NIVEL + MENSAJE
    # ==================================================

    level = calculate_level(score_norm)
    message = build_message(level)

    # ==================================================
    # 📊 SCORE FINAL (0–100 VISUAL)
    # ==================================================

    score_visual = int(score_norm * 100)

    # ==================================================
    # 🧠 CONFIANZA
    # ==================================================

    confidence = calculate_confidence(result)

    # ==================================================
    # 📦 RESPONSE
    # ==================================================

    response = {
        "analysis_key": analysis_key,
        "url": req.url,
        "level": level,
        "score": score_visual,
        "confidence": confidence,
        "message": message,
        "details": result.get("reasons", []),
        "timestamp": int(time.time())
    }

    return response


# ======================================================
# 🩺 HEALTH CHECK
# ======================================================

@app.get("/")
def root():
    return {"status": "SignalCheck API running"}