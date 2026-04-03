print("APP FILE ACTUAL 14.1 - PRO UX LAYER ENABLED")

import os
import json
import traceback
from datetime import datetime

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
from backend.final_adjustment import apply_context_adjustment, build_summary
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

API_VERSION    = "v3"
ENGINE_VERSION = "v14.1"
PROMPT_VERSION = "v3"

PLAN_LIMITS = {
    "free":       50,
    "pro":         0,
    "enterprise":  0,
}

app = FastAPI(title="GE SignalCheck API — v14.1")

# =========================
# 🔥 PRO LAYER (NUEVO)
# =========================
def build_pro_layer(signals, commercial_risk, score):

    # 🧨 ALERTA
    if commercial_risk.get("level") == "alto":
        alert = "Patrón típico de riesgo comercial detectado"
    elif score >= 0.55:
        alert = "Alta presión narrativa detectada"
    elif score >= 0.25:
        alert = "Señales mixtas, requiere lectura crítica"
    else:
        alert = "Contenido estructuralmente estable"

    # 🧠 INTERPRETACIÓN
    if "urgency" in " ".join(signals).lower():
        interpretation = "El contenido intenta generar urgencia para reducir el análisis crítico."
    elif "promises" in " ".join(signals).lower():
        interpretation = "Se detectan afirmaciones fuertes que pueden no estar respaldadas."
    else:
        interpretation = "El contenido presenta patrones estructurales que pueden influir en la interpretación."

    # 🎯 ACCIÓN
    if commercial_risk.get("level") in ["medio", "alto"]:
        action = "Evitar pagos directos o decisiones sin verificar la fuente."
    elif score >= 0.5:
        action = "No tomar decisiones inmediatas. Verificar información antes de actuar."
    else:
        action = "Leer con criterio crítico y validar fuentes si es necesario."

    # 🧩 PERFIL
    if commercial_risk.get("level") == "alto":
        profile = "Contenido comercial de alto riesgo"
    elif score >= 0.55:
        profile = "Contenido con presión narrativa significativa"
    elif score >= 0.25:
        profile = "Contenido con señales mixtas"
    else:
        profile = "Contenido estructuralmente estable"

    return {
        "alert": alert,
        "interpretation": interpretation,
        "action": action,
        "content_profile": profile
    }

# =========================
# 🔐 RATE LIMIT
# =========================
def get_rate_key(request: Request):
    ext = request.headers.get("x-extension-id")
    if ext:
        return f"ext:{ext}"
    return get_remote_address(request)

limiter = Limiter(key_func=get_rate_key)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intente más tarde."}
    )

# =========================
# 🔐 CORS
# =========================
env_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "chrome-extension://ooigpgpbfjefbdjmhjpnmmakieioplc"
)

allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# =========================
# MODELS
# =========================
class VerifyRequest(BaseModel):
    url: str
    text: str

@app.get("/")
def root():
    return {"status": "GE SignalCheck API online", "engine": ENGINE_VERSION}

@app.get("/health")
def health():
    return {"status": "ok", "engine": ENGINE_VERSION}

# =========================
# ENDPOINT
# =========================
@app.post("/v3/verify")
@limiter.limit("20/minute")
async def verify(
    request: Request,
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    x_pro_token: str = Header(None),
    db: Session = Depends(get_db)
):

    user_agent = request.headers.get("user-agent", "").lower()
    if any(bot in user_agent for bot in ["curl", "python", "wget", "httpclient"]):
        raise HTTPException(status_code=403, detail="Cliente bloqueado")

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension = db.query(Extension).filter(
        Extension.extension_id == x_extension_id.strip()
    ).first()

    if not extension:
        extension = Extension(
            extension_id=x_extension_id.strip(),
            is_active=True,
            plan="free",
            analyses_used=0,
            analyses_limit=PLAN_LIMITS["free"],
            pro_token=None
        )
        db.add(extension)
        db.commit()
        db.refresh(extension)

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    if x_pro_token:
        if extension.pro_token and x_pro_token == extension.pro_token:
            extension.plan = "pro"
        else:
            extension.plan = "free"

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    if len(data.text) > 20000:
        raise HTTPException(status_code=400, detail="Texto demasiado largo")

    text = data.text
    url  = data.url or ""

    content_hash = generate_content_hash(text)
    analysis_key = build_analysis_key(
        url=url,
        content_hash=content_hash,
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION
    )

    cached_log = db.query(AnalysisLog).filter(
        AnalysisLog.analysis_key == analysis_key
    ).first()

    if cached_log and cached_log.response_json:
        try:
            cached_response = json.loads(cached_log.response_json)
            cached_response["meta"]["cached"] = True
            cached_response["meta"]["plan"]   = extension.plan
            return cached_response
        except Exception:
            pass

    try:
        result = analyze_context(text, url)
        result = apply_context_adjustment(result)

        score = float(result.get("score", 0))
        adjusted_level = result.get("level", "yellow")

    except Exception as e:
        print("🔥 ERROR:", traceback.format_exc())
        result = {"signals": []}
        score = 0
        adjusted_level = "yellow"

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada",
            "orientation": "alerta"
        }
        for s in result.get("signals", [])[:5]
    ]

    pro_layer = build_pro_layer(
        signals=result.get("signals", []),
        commercial_risk=result.get("commercial_risk", {}),
        score=score
    )

    response_payload = {
        "analysis": {
            "level": adjusted_level,
            "summary": build_summary(result),
            "confidence": result.get("confidence", 0),
            "context": result.get("context", "general"),
            "indicators": indicators,
            "structural_index": score,
            "pro": pro_layer
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key": analysis_key,
            "cached": False,
            "plan": extension.plan
        }
    }

    db.add(AnalysisLog(
        risk_index=score,
        level=adjusted_level,
        engine_version=ENGINE_VERSION,
        analysis_key=analysis_key,
        response_json=json.dumps(response_payload)
    ))

    db.commit()

    return response_payload