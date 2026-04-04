print("APP FILE ACTUAL 14.3 - PRO FROM ENGINE + SCORE 0-100")

import os
import json
import traceback

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.database import engine, get_db
from backend.models import Base, Extension, AnalysisLog
from backend.engine import analyze_context
from backend.final_adjustment import apply_context_adjustment
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

ENGINE_VERSION = "v14.3"

# =========================
# RATE LIMIT
# =========================
def get_rate_key(request: Request):
    ext = request.headers.get("x-extension-id")
    return f"ext:{ext}" if ext else get_remote_address(request)

limiter = Limiter(key_func=get_rate_key)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc):
    return JSONResponse(status_code=429, content={"detail": "Demasiadas solicitudes"})

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# =========================
# MODELO
# =========================
class VerifyRequest(BaseModel):
    url: str
    text: str

# =========================
# ENDPOINT
# =========================
@app.post("/v3/verify")
@limiter.limit("20/minute")
async def verify(
    request: Request,
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    text = data.text
    url  = data.url or ""

    content_hash = generate_content_hash(text)
    analysis_key = build_analysis_key(url, content_hash, ENGINE_VERSION, "v3")

    cached = db.query(AnalysisLog).filter(AnalysisLog.analysis_key == analysis_key).first()
    if cached:
        return json.loads(cached.response_json)

    try:
        result = analyze_context(text, url)
        result = apply_context_adjustment(result)

        score = float(result.get("score", 0))
        signals = result.get("signals", [])

    except Exception:
        score = 0
        signals = []

    # =========================
    # NORMALIZACIÓN
    # engine v13.8 devuelve score como float 0-1
    # app lo convierte a entero 0-100 y normaliza level
    # =========================
    score_int = int(round(score * 100)) if score <= 1.0 else int(score)

    if score < 0.20:
        level   = "green"
        summary = "El contenido no presenta patrones estructurales de riesgo."
    elif score < 0.55:
        level   = "yellow"
        summary = "El contenido requiere lectura crítica."
    else:
        level   = "red"
        summary = "Se detecta presión narrativa significativa."

    indicators = [{"title": s} for s in signals[:5]]

    # PRO viene del engine — rico y estructurado
    pro = result.get("pro", {})

    response = {
        "analysis": {
            "level":            level,
            "summary":          summary,
            "message":          result.get("message", summary),
            "insight":          result.get("insight", ""),
            "score":            score_int,
            "confidence":       result.get("confidence", 0),
            "context":          result.get("context", "general"),
            "source_type":      result.get("source_type", "unknown"),
            "signals":          signals[:6],
            "indicators":       indicators,
            "commercial_risk":  result.get("commercial_risk", {}),
            "pro":              pro,
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key":   analysis_key,
            "plan":           "free"
        }
    }

    db.add(AnalysisLog(
        risk_index=score,
        level=level,
        engine_version=ENGINE_VERSION,
        analysis_key=analysis_key,
        response_json=json.dumps(response)
    ))
    db.commit()

    return response