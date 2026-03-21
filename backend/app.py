print("APP FILE ACTUAL 11.8 - error safe mode activo")

# ==========================================================
# IMPORTS
# ==========================================================

import os
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

API_VERSION = "v3"
ENGINE_VERSION = "v8.6"
PROMPT_VERSION = "none"

# ==========================================================
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="GE SignalCheck API v8 - Stable")

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 para desarrollo (clave)
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
            analyses_limit=0
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

    # ==========================================================
    # 🔥 BLOQUE PROTEGIDO (CLAVE)
    # ==========================================================

    try:
        result = analyze_context(text, url)

        result = apply_context_adjustment(result)
        summary = build_summary(result)

        status_color = result.get("status", "neutral")
        level = result.get("label", "indeterminado")

    except Exception as e:
        print("🔥 ERROR EN ANALISIS:", str(e))

        result = {
            "score": 0,
            "signals": [],
            "status": "neutral",
            "label": "error",
            "context_note": "No se pudo analizar el contenido"
        }

        summary = "No se pudo completar el análisis."
        status_color = "neutral"
        level = "error"

    # ==========================================================
    # GUARDADO
    # ==========================================================

    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else "unknown"

    analysis_log = AnalysisLog(
        trust_score=result.get("score", 0),
        rhetorical_score=0,
        narrative_score=0,
        absence_score=0,
        risk_index=result.get("score", 0),
        level=level,
        premium_requested=False,
        engine_version=ENGINE_VERSION,
        analysis_key=analysis_key,
        domain=domain,
        created_at=datetime.utcnow()
    )

    db.add(analysis_log)
    extension.analyses_used += 1
    db.commit()

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    return {
        "analysis": {
            "level": level,
            "summary": summary,
            "indicators": indicators,
            "shown_indicators": len(indicators),
            "structural_index": result.get("score", 0),
            "context_note": result.get("context_note", "")
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "analysis_key": analysis_key,
            "cached": False,
            "plan": extension.plan,
            "disclaimer": "SignalCheck no determina veracidad."
        }
    }