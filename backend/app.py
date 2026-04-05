# ======================================================
# SIGNALCHECK API – APP.PY (FIX ENGINE INTEGRATION)
# ======================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time

# 🔥 IMPORT REAL (CORRECTO)
from backend.engine import analyze_context

app = FastAPI()

# ======================================================
# 🌐 CORS
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


def map_level(engine_level: str) -> str:
    # engine usa: red / yellow / green
    if engine_level == "red":
        return "alto"
    elif engine_level == "yellow":
        return "moderado"
    return "bajo"


# ======================================================
# 🚀 ENDPOINT
# ======================================================

@app.post("/v3/verify")
async def verify(req: VerifyRequest, request: Request):

    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no autorizada")

    # 🔑 KEY
    analysis_key = generate_analysis_key(req.url, req.text)

    # ==================================================
    # 🧠 ENGINE (USO CORRECTO)
    # ==================================================

    try:
        result = analyze_context(req.text, req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ==================================================
    # 🎯 DATOS DEL ENGINE
    # ==================================================

    raw_score = result.get("score", 0)
    engine_level = result.get("level", "green")

    level = map_level(engine_level)

    # 🔥 YA VIENE EN 0–100 → NO TOCAR
    score_visual = int(raw_score)

    confidence = int(result.get("confidence", 0) * 100)

    message = result.get("message", "")

    # ==================================================
    # 📦 RESPONSE FINAL
    # ==================================================

    return {
        "analysis_key": analysis_key,
        "url": req.url,
        "level": level,
        "score": score_visual,
        "confidence": confidence,
        "message": message,
        "details": result.get("signals", []),
        "pro": result.get("pro", {}),
        "timestamp": int(time.time())
    }


# ======================================================
# 🩺 HEALTH CHECK
# ======================================================

@app.get("/")
def root():
    return {"status": "SignalCheck API running"}