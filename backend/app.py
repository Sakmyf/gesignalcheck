print("APP FILE ACTUAL 9.9")

# ==========================================================
# CORE IMPORTS
# ==========================================================

from backend.engine import analyze_context, interpret_score
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

import re
import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import engine, get_db
from backend.models import Base, Extension

# ==========================================================
# DB INIT
# ==========================================================

Base.metadata.create_all(bind=engine)

# ==========================================================
# PDF IMPORTS
# ==========================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

# ==========================================================
# VERSION CONTROL
# ==========================================================

ENGINE_VERSION = "v8.5"
PROMPT_VERSION = "none"  # Free mode no usa IA generativa

# ==========================================================
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="GE SignalCheck API v8 - Versioned Infrastructure Ready")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# MODELO DE ENTRADA
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
# ENDPOINT PUBLICO
# ==========================================================

@app.post("/v3/verify")
async def verify(
    data: VerifyRequest,
    x_extension_id: str = Header(None),
    db: Session = Depends(get_db)
):

    # -------------------------
    # VALIDACION EXTENSION (DB REAL)
    # -------------------------

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    extension = db.query(Extension).filter(
        Extension.extension_id == x_extension_id.strip()
    ).first()

    if not extension:
        raise HTTPException(status_code=401, detail="Extensión no registrada")

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    # Si analyses_limit es 0 => ilimitado
    if extension.analyses_limit > 0 and \
       extension.analyses_used >= extension.analyses_limit:
        raise HTTPException(status_code=403, detail="Límite de uso alcanzado")

    # -------------------------
    # VALIDACION TEXTO
    # -------------------------

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    # -------------------------
    # DETERMINAR SITE TYPE
    # -------------------------

    parsed = urlparse(data.url or "")
    site_type = parsed.netloc if parsed.netloc else "unknown"

    # -------------------------
    # VERSIONADO / TRAZABILIDAD
    # -------------------------

    content_hash = generate_content_hash(data.text)

    analysis_key = build_analysis_key(
        url=data.url or "",
        content_hash=content_hash,
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION,
    )

    # -------------------------
    # ANALISIS PRINCIPAL
    # -------------------------

    result = analyze_context(data.text, data.url or "")
    status_color, level = interpret_score(result["score"])

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada durante el análisis contextual.",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    # -------------------------
    # INCREMENTAR USO
    # -------------------------

    extension.analyses_used += 1
    db.commit()

    # -------------------------
    # RESPUESTA FINAL
    # -------------------------

    return {
        "analysis": {
            "level": level,
            "summary": "requiere lectura crítica",
            "indicators": indicators,
            "shown_indicators": len(indicators),
            "note": "Se muestran las señales estructurales más relevantes para esta evaluación."
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "site_type": site_type,
            "content_hash": content_hash,
            "analysis_key": analysis_key,
            "premium_available": True,
            "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
        }
    }

# ==========================================================
# ENDPOINT PREMIUM JSON
# ==========================================================

@app.post("/v3/verify/premium")
async def verify_premium(
    data: VerifyRequest,
    x_premium_token: str = Header(None)
):

    if not x_premium_token:
        raise HTTPException(status_code=401, detail="Acceso premium requerido")

    return {
        "analysis": {
            "level": "bajo",
            "structural_index": 0.25,
            "breakdown": {},
            "all_detected_signals": ["estructura clara"],
            "critical_questions": [
                "¿Las afirmaciones principales incluyen respaldo verificable?",
                "¿Existen fuentes alternativas que aporten contexto adicional?",
                "¿El lenguaje prioriza impacto emocional sobre evidencia estructural?"
            ]
        }
    }

# ==========================================================
# ENDPOINT PDF PREMIUM
# ==========================================================

@app.post("/v3/report")
async def generate_report(
    data: VerifyRequest,
    x_premium_token: str = Header(None)
):

    if not x_premium_token:
        raise HTTPException(status_code=401, detail="Acceso premium requerido")

    return {"status": "PDF endpoint activo"}