print("VERSION EXTENSION-ID ACTIVA")

import re
import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
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
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="GE SignalCheck API v7 - Production Stable")

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
async def verify(request: Request, data: VerifyRequest):

    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    if extension_id.strip() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    if len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    # RESPUESTA ESTABLE PARA TEST
    return {
        "analysis": {
            "level": "bajo",
            "summary": "No se observan concentraciones significativas de señales estructurales.",
            "indicators": [
                {
                    "title": "estructura clara",
                    "explanation": "Indicador estructural observado durante el análisis automatizado.",
                    "orientation": "neutro"
                },
                {
                    "title": "tono neutro",
                    "explanation": "Indicador estructural observado durante el análisis automatizado.",
                    "orientation": "neutro"
                }
            ],
            "shown_indicators": 2,
            "note": "Se muestran los indicadores estructurales más relevantes para esta evaluación."
        },
        "meta": {
            "premium_available": True,
            "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
        }
    }


# ==========================================================
# ENDPOINT PREMIUM JSON
# ==========================================================

@app.post("/v3/verify/premium")
async def verify_premium(request: Request, data: VerifyRequest):

    premium_token = request.headers.get("x-premium-token")

    if not premium_token:
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
async def generate_report(request: Request, data: VerifyRequest):

    premium_token = request.headers.get("x-premium-token")

    if not premium_token:
        raise HTTPException(status_code=401, detail="Acceso premium requerido")

    return {"status": "PDF endpoint activo"}