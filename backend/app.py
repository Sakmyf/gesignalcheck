print("APP FILE ACTUAL 14.2 - COHERENCE FIX + PRO IMPROVED")

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

ENGINE_VERSION = "v14.2"

app = FastAPI(title="GE SignalCheck API — v14.2")

# =========================
# 🔥 PRO LAYER MEJORADO
# =========================
def build_pro_layer(signals, commercial_risk, score):

    text = " ".join(signals).lower()

    # 🧨 ALERTA
    if commercial_risk.get("level") == "alto":
        alert = "Patrón típico de riesgo comercial detectado"
    elif score >= 0.55:
        alert = "Alta presión narrativa detectada"
    elif score >= 0.25:
        alert = "Señales mixtas detectadas"
    else:
        alert = "Contenido estructuralmente estable"

    # 🧠 INTERPRETACIÓN (DINÁMICA)
    if "urgency" in text:
        interpretation = "Se detecta presión para generar decisiones rápidas."
    elif "emotion" in text:
        interpretation = "El contenido busca generar una reacción emocional."
    elif "polarization" in text:
        interpretation = "Se presenta un enfoque polarizado del mensaje."
    elif "misinformation" in text:
        interpretation = "Se detectan posibles inconsistencias o falta de respaldo."
    elif "commercial" in text:
        interpretation = "Patrón típico de contenido comercial con riesgo."
    else:
        interpretation = "Estructura informativa sin señales críticas fuertes."

    # 🎯 ACCIÓN
    if commercial_risk.get("level") in ["medio", "alto"]:
        action = "Evitar pagos o decisiones sin verificar la fuente."
    elif score >= 0.5:
        action = "Tomar distancia y verificar antes de actuar."
    else:
        action = "Consumir con criterio crítico."

    # 🧩 PERFIL
    if commercial_risk.get("level") == "alto":
        profile = "Contenido comercial de alto riesgo"
    elif score >= 0.55:
        profile = "Contenido con presión narrativa"
    elif score >= 0.25:
        profile = "Contenido mixto"
    else:
        profile = "Contenido informativo estable"

    return {
        "alert": alert,
        "interpretation": interpretation,
        "action": action,
        "content_profile": profile
    }

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
    # 🔥 NORMALIZACIÓN CLAVE
    # =========================
    if score < 0.20:
        level = "bajo"
        summary = "El contenido no presenta patrones estructurales de riesgo."
    elif score < 0.55:
        level = "medio"
        summary = "El contenido requiere lectura crítica."
    else:
        level = "alto"
        summary = "Se detecta presión narrativa significativa."

    indicators = [{"title": s} for s in signals[:5]]

    pro = build_pro_layer(
        signals=signals,
        commercial_risk=result.get("commercial_risk", {}),
        score=score
    )

    response = {
        "analysis": {
            "level": level,
            "summary": summary,
            "confidence": result.get("confidence", 0),
            "context": result.get("context", "general"),
            "indicators": indicators,
            "structural_index": score,
            "pro": pro
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key": analysis_key,
            "plan": "free"
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