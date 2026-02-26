print("APP FILE ACTUAL 3.4")

from backend.engine import analyze_context, interpret_score
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

import re
import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import TableStyle


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
# EXTENSIONES AUTORIZADAS
# ==========================================================

ALLOWED_EXTENSIONS = [
    "fijnjbaacmpnhaaconoafbmnholbmaig"
]

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
    x_extension_id: str = Header(None)
):

    # -------------------------
    # VALIDACIONES DE SEGURIDAD
    # -------------------------

    if not x_extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    if x_extension_id.strip() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    if len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    # -------------------------
    # ANALISIS PRINCIPAL
    # -------------------------

    analysis = analyze_context(data.text, data.url)

    # Si analyze_context no devuelve site_type,
    # lo determinamos desde la URL
    parsed = urlparse(data.url)
    site_type = parsed.netloc if parsed.netloc else "unknown"

    # -------------------------
    # VERSIONADO / TRAZABILIDAD
    # -------------------------

    content_hash = generate_content_hash(data.text)
    content_hash = generate_content_hash(data.text)

analysis_key = build_analysis_key(
    url=data.url or "",
    content_hash=content_hash,
    engine_version=ENGINE_VERSION,
    prompt_version=PROMPT_VERSION,
)

    meta = {
        "engine_version": "5.0",
        "site_type": site_type,
        "content_hash": content_hash,
        "analysis_key": analysis_key,
        "premium_available": True,
        "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
    }

    # -------------------------
    # RESPUESTA FINAL
    # -------------------------

    return {
        "analysis": analysis,
        "meta": meta
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