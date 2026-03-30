print("APP FILE ACTUAL 13.8 - SECURE PRODUCTION READY")

import os
import json
import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 🔐 RATE LIMIT
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
ENGINE_VERSION = "v13.8"
PROMPT_VERSION = "v3"

PLAN_LIMITS = {
    "free":       50,
    "pro":         0,
    "enterprise":  0,
}

app = FastAPI(title="GE SignalCheck API — v13.8")

# =========================
# 🔐 RATE LIMIT KEY (MEJORADO)
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
# 🔥 ENDPOINT PROTEGIDO
# =========================
@app.post("/v3/verify")
@limiter.limit("20/minute")
async def verify(
    request: Request,
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):

    # 🔐 BLOQUEO BOT BÁSICO
    user_agent = request.headers.get("user-agent", "").lower()
    if any(bot in user_agent for bot in ["curl", "python", "wget", "httpclient"]):
        raise HTTPException(status_code=403, detail="Cliente bloqueado")

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension = db.query(Extension).filter(
        Extension.extension_id == x_extension_id.strip()
    ).first()

    # 🧠 AUTO-REGISTRO
    if not extension:
        extension = Extension(
            extension_id=x_extension_id.strip(),
            is_active=True,
            plan="pro",
            analyses_used=0,
            analyses_limit=PLAN_LIMITS["free"]
        )
        db.add(extension)
        db.commit()
        db.refresh(extension)

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    # 🔐 VALIDACIONES
    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    if len(data.text) > 20000:
        raise HTTPException(status_code=400, detail="Texto demasiado largo")

    text = data.text
    url  = data.url or ""

    # 🔐 CACHE KEY
    content_hash = generate_content_hash(text)
    analysis_key = build_analysis_key(
        url=url,
        content_hash=content_hash,
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION
    )

    # 🔁 CACHE HIT
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

    # 🔐 LÍMITE POR PLAN
    if extension.analyses_limit > 0 and extension.analyses_used >= extension.analyses_limit:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "limite_alcanzado",
                "used":  extension.analyses_used,
                "limit": extension.analyses_limit,
                "plan":  extension.plan,
            }
        )

    # 🧠 ANALYSIS
    try:
        result = analyze_context(text, url)
        result = apply_context_adjustment(result)

        score = float(result.get("score", 0))

        _LEVEL_MAP = {
            "green":  ("green",  "bajo"),
            "yellow": ("yellow", "medio"),
            "red":    ("red",    "alto"),
        }

        adjusted_level      = result.get("level", "yellow")
        status_color, level = _LEVEL_MAP.get(adjusted_level, ("yellow", "medio"))

        summary    = build_summary(result)
        insight    = result.get("insight", "")
        confidence = result.get("confidence", 0.0)
        context    = result.get("context", "general")

    except Exception as e:
        print("🔥 ERROR EN ANALISIS:", traceback.format_exc())

        score        = 0.0
        result       = {"score": 0, "signals": []}
        summary      = f"Error interno: {str(e)}"
        insight      = ""
        confidence   = 0.0
        context      = "general"
        status_color = "yellow"
        level        = "medio"

    indicators = [
        {
            "title":       s,
            "explanation": "Señal estructural detectada",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    response_payload = {
        "analysis": {
            "level":            level,
            "summary":          summary,
            "insight":          insight,
            "confidence":       confidence,
            "context":          context,
            "indicators":       indicators,
            "shown_indicators": len(indicators),
            "structural_index": score,
            "status_color":     status_color,
            "pro":              result.get("pro", {})
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key":   analysis_key,
            "cached":         False,
            "plan":           extension.plan,
            "disclaimer":     "SignalCheck no determina veracidad."
        }
    }

    # 💾 GUARDADO
    try:
        analysis_log = AnalysisLog(
            risk_index       = score,
            level            = level,
            engine_version   = ENGINE_VERSION,
            analysis_key     = analysis_key,
            response_json    = json.dumps(response_payload)
        )

        db.add(analysis_log)
        extension.analyses_used += 1
        db.commit()

    except Exception as db_error:
        print("⚠️ ERROR GUARDANDO EN DB:", str(db_error))

    return response_payload