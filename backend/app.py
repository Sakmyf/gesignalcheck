print("APP FILE ACTUAL 13.6 - engine v13.6 integrated")

import os
import json
import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from backend.database import engine, get_db
from backend.models import Base, Extension, AnalysisLog
from backend.engine import analyze_context
from backend.final_adjustment import apply_context_adjustment, build_summary
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

API_VERSION    = "v3"
# 🔥 FIX: Sincronizado con engine.py para evitar errores de caché
ENGINE_VERSION = "v13.6"
PROMPT_VERSION = "v3"

PLAN_LIMITS = {
    "free":       50,
    "pro":         0,
    "enterprise":  0,
}

app = FastAPI(title="GE SignalCheck API — v13.6")

# 🔥 FIX: CORS Seguro leyendo desde las variables de entorno (o por defecto tu extensión)
env_origins = os.getenv("ALLOWED_ORIGINS", "chrome-extension://ooigpgpbfjefbdjmhjpnmmakieioplc")
allowed_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # Ya no está abierto a "*"
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

class VerifyRequest(BaseModel):
    url: str
    text: str

@app.get("/")
def root():
    return {"status": "GE SignalCheck API online", "engine": ENGINE_VERSION}

@app.get("/health")
def health():
    return {"status": "ok", "engine": ENGINE_VERSION}

@app.post("/v3/verify")
async def verify(
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):
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
            analyses_limit=PLAN_LIMITS["free"]
        )
        db.add(extension)
        db.commit()
        db.refresh(extension)

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

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
        error_details = traceback.format_exc()
        print("🔥 ERROR EN ANALISIS:", error_details)
        
        score        = 0.0
        result       = {"score": 0, "signals": [], "context_note": "Error en análisis"}
        # 🔥 Ahora la extensión nos mostrará exactamente qué se rompió:
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
            "context_note":     result.get("context_note", ""),
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

    _s = result.get("pro", {}).get("_scores", {})

    try:
        analysis_log = AnalysisLog(
            trust_score      = _s.get("source_trust",   0.0),
            narrative_score  = _s.get("credibility",    0.0),
            rhetorical_score = _s.get("misinformation", 0.0),
            absence_score    = _s.get("urgency",        0.0),
            risk_index       = score,
            level            = level,
            premium_requested= False,
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