from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import hashlib

# 🔥 IMPORT CORRECTO (ADAPTADO A TU ENGINE)
from backend.engine import analyze_context

app = FastAPI()

# =========================
# RATE LIMIT
# =========================
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda r, e: HTTPException(429, "Rate limit exceeded"))
app.add_middleware(SlowAPIMiddleware)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HELPERS
# =========================

def normalize_engine_output(result: dict):

    score = result.get("score", 0)
    confidence = result.get("confidence", 0.5)

    # 🔥 FIX: evitar 0 absoluto
    if confidence == 0:
        confidence = 0.45

    # normalizar score a 0-1
    score_norm = max(0, min(score / 100, 1))

    return score_norm, confidence


def get_level(score: float):

    if score <= 0.2:
        return "bajo"
    elif score <= 0.6:
        return "moderado"
    else:
        return "alto"


# =========================
# ENDPOINT PRINCIPAL
# =========================

@app.post("/v3/verify")
@limiter.limit("30/minute")
async def verify(request: Request):

    data = await request.json()

    text = data.get("text", "")
    url = data.get("url", "")
    title = data.get("title", "")

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    # =========================
    # ANALYSIS KEY (determinístico)
    # =========================
    raw_key = f"{url}|{text[:500]}"
    analysis_key = hashlib.sha256(raw_key.encode()).hexdigest()

    # =========================
    # ENGINE CALL
    # =========================
    result = analyze_context(text, url, title)

    # =========================
    # NORMALIZACIÓN
    # =========================
    score_norm, confidence = normalize_engine_output(result)

    # =========================
    # NIVEL FINAL
    # =========================
    level = get_level(score_norm)

    # 🔥 FIX CRÍTICO
    if score_norm == 0:
        level = "bajo"

    # =========================
    # RESPONSE
    # =========================
    return {
        "analysis_key": analysis_key,
        "score": int(score_norm * 100),
        "level": level,
        "confidence": round(confidence * 100),
        "message": result.get("message", ""),
        "signals": result.get("signals", []),
        "insight": result.get("insight", ""),
        "context": result.get("context", ""),
        "source_type": result.get("source_type", ""),
        "pro": result.get("pro", {})
    }