print("APP FILE ACTUAL 12.0 - calibrated scoring FIXED")

# ==========================================================
# IMPORTS
# ==========================================================

import os
import json
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

# ==========================================================
# VERSION CONTROL
# ==========================================================

API_VERSION    = "v3"
ENGINE_VERSION = "v9.6"
PROMPT_VERSION = "none"

# ==========================================================
# PLAN LIMITS (P1-C)
# 0 = sin límite (pro / enterprise / beta abierta)
# ==========================================================

PLAN_LIMITS = {
    "free":       50,
    "pro":         0,
    "enterprise":  0,
}

# ==========================================================
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="GE SignalCheck API v8 - Stable")

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # desarrollo abierto
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# DB INIT
# ==========================================================

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# ==========================================================
# INPUT MODEL
# ==========================================================

class VerifyRequest(BaseModel):
    url: str
    text: str

# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():
    return {"status": "GE SignalCheck API online"}

# ==========================================================
# VERIFY ENDPOINT
# ==========================================================

@app.post("/v3/verify")
async def verify(
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):

    # ======================================================
    # VALIDACIÓN EXTENSIÓN
    # ======================================================

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension = db.query(Extension).filter(
        Extension.extension_id == x_extension_id.strip()
    ).first()

    # AUTO REGISTRO
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

    # ======================================================
    # HASH + CACHE KEY
    # ======================================================

    content_hash = generate_content_hash(text)

    analysis_key = build_analysis_key(
        url=url,
        content_hash=content_hash,
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION
    )

    # ======================================================
    # CACHE LOOKUP (P1-A)
    # Si existe un log con este key y tiene response_json guardado
    # → retornar directo. No corre el análisis, no toca analyses_used.
    # El plan en meta se actualiza al plan actual por si cambió.
    # ======================================================

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
            pass  # JSON corrupto → continuar con análisis fresco

    # ======================================================
    # LIMIT CHECK (P1-C)
    # Solo corre si no hubo cache hit.
    # 0 = sin límite (pro / enterprise / beta).
    # ======================================================

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

    # ======================================================
    # 🔥 ANALYSIS CORE (PROTEGIDO)
    # ======================================================

    try:
        result = analyze_context(text, url)

        # Ajuste final
        result = apply_context_adjustment(result)

        # Score limpio
        score = float(result.get("score", 0))

        # ==================================================
        # FIX P0: respetar el nivel ajustado por apply_context_adjustment.
        # Antes se recalculaba desde score → borraba upgrades green→yellow.
        # El engine ya clasifica por los mismos umbrales (0.30 / 0.60),
        # apply_context_adjustment puede subir el nivel → hay que leerlo.
        # ==================================================

        _LEVEL_MAP = {
            "green":  ("green",  "bajo"),
            "yellow": ("yellow", "medio"),
            "red":    ("red",    "alto"),
        }
        adjusted_level               = result.get("level", "yellow")
        status_color, level          = _LEVEL_MAP.get(adjusted_level, ("yellow", "medio"))

        summary = build_summary(result)

    except Exception as e:
        print("🔥 ERROR EN ANALISIS:", str(e))

        score = 0.0
        result = {
            "score": 0,
            "signals": [],
            "context_note": "No se pudo analizar el contenido"
        }

        summary = "No se pudo completar el análisis."
        status_color = "yellow"
        level = "medio"

    # ======================================================
    # INDICADORES
    # ======================================================

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    # ======================================================
    # RESPONSE FINAL (P1-A)
    # Extraído como variable para poder serializarlo al guardar en DB.
    # ======================================================

    response_payload = {
        "analysis": {
            "level":            level,
            "summary":          summary,
            "indicators":       indicators,
            "shown_indicators": len(indicators),
            "structural_index": score,
            "context_note":     result.get("context_note", ""),
            "status_color":     status_color
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key":   analysis_key,
            "cached":         False,
            "plan":           extension.plan,
            "disclaimer":     "SignalCheck no determina veracidad."
        }
    }

    # ======================================================
    # GUARDADO DB
    # ======================================================

    # Leer scores individuales del engine (P1-B).
    # Fallback a 0.0 si el campo no existe (ej: error en análisis).
    _s = result.get("_scores", {})

    try:
        analysis_log = AnalysisLog(
            trust_score      = _s.get("source_trust",   0.0),
            narrative_score  = _s.get("narrative",      0.0),
            rhetorical_score = _s.get("rhetorical",     0.0),
            absence_score    = _s.get("urgency",        0.0),
            risk_index       = score,
            level            = level,
            premium_requested= False,
            engine_version   = ENGINE_VERSION,
            analysis_key     = analysis_key,
            response_json    = json.dumps(response_payload)  # P1-A
        )

        db.add(analysis_log)
        extension.analyses_used += 1
        db.commit()

    except Exception as db_error:
        print("⚠️ ERROR GUARDANDO EN DB:", str(db_error))

    return response_payload