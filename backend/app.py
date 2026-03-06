print("APP FILE ACTUAL 11.4 - dashboard HTML enabled - stable")

# ==========================================================
# IMPORTS
# ==========================================================

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from backend.database import engine, get_db
from backend.models import Base, Extension, AnalysisLog
from backend.engine import analyze_context, interpret_score
from backend.utils.content_versioning import (
    generate_content_hash,
    build_analysis_key,
)

# ==========================================================
# VERSION CONTROL
# ==========================================================

ENGINE_VERSION = "v8.5"
PROMPT_VERSION = "none"

# ==========================================================
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="GE SignalCheck API v8 - Stable")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# TEMPLATES CONFIG (IMPORTANTE)
# ==========================================================

templates = Jinja2Templates(directory="../templates")

# ==========================================================
# DB INIT (SAFE STARTUP INIT)
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
# VERIFY ENDPOINT (NO TOCADO)
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

    if not extension:
        raise HTTPException(status_code=401, detail="Extensión no registrada")

    if not extension.is_active:
        raise HTTPException(status_code=403, detail="Extensión desactivada")

    if extension.analyses_limit > 0 and \
       extension.analyses_used >= extension.analyses_limit:
        raise HTTPException(status_code=403, detail="Límite de uso alcanzado")

    plan_normalized = extension.plan.lower()

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    text = data.text
    url = data.url or ""

    content_hash = generate_content_hash(text)

    analysis_key = build_analysis_key(
        url=url,
        content_hash=content_hash,
        engine_version=ENGINE_VERSION,
        prompt_version=PROMPT_VERSION
    )

    existing_log = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.analysis_key == analysis_key)
        .first()
    )

    if existing_log:
        return {
            "analysis": {
                "level": existing_log.level,
                "summary": "Resultado recuperado desde cache.",
                "indicators": [],
                "shown_indicators": 0,
                "note": "Este análisis ya había sido procesado anteriormente.",
                "structural_index": existing_log.risk_index
            },
            "meta": {
                "engine_version": existing_log.engine_version,
                "analysis_key": analysis_key,
                "cached": True,
                "premium_available": True,
                "plan": plan_normalized,
                "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
            }
        }

    result = analyze_context(text, url)
    status_color, level = interpret_score(result.get("score", 0))

    parsed = urlparse(url)
    site_type = parsed.netloc if parsed.netloc else "unknown"

    analysis_log = AnalysisLog(
        trust_score=result.get("quality_score", 0),
        rhetorical_score=0,
        narrative_score=0,
        absence_score=0,
        risk_index=result.get("score", 0),
        level=level,
        premium_requested=False,
        engine_version=ENGINE_VERSION,
        analysis_key=analysis_key
    )

    db.add(analysis_log)
    extension.analyses_used += 1
    db.commit()

    indicators = [
        {
            "title": s,
            "explanation": "Señal estructural detectada durante el análisis contextual.",
            "orientation": "alerta" if status_color != "green" else "neutro"
        }
        for s in result.get("signals", [])[:5]
    ]

    return {
        "analysis": {
            "level": level,
            "summary": result.get("label"),
            "indicators": indicators,
            "shown_indicators": len(indicators),
            "note": "Se muestran las señales estructurales más relevantes para esta evaluación.",
            "structural_index": result.get("score", 0)
        },
        "meta": {
            "engine_version": ENGINE_VERSION,
            "site_type": site_type,
            "content_hash": content_hash,
            "analysis_key": analysis_key,
            "cached": False,
            "premium_available": True,
            "plan": plan_normalized,
            "disclaimer": "SignalCheck no determina veracidad. Ningún sistema automatizado reemplaza el juicio humano."
        }
    }

# ==========================================================
# DASHBOARD JSON (SE MANTIENE)
# ==========================================================

@app.get("/v3/dashboard/{analysis_key}")
async def dashboard_view(analysis_key: str, db: Session = Depends(get_db)):

    log = db.query(AnalysisLog).filter(
        AnalysisLog.analysis_key == analysis_key
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return {
        "analysis_key": analysis_key,
        "engine_version": log.engine_version,
        "level": log.level,
        "structural_index": log.risk_index,
        "trust_score": log.trust_score,
        "rhetorical_score": log.rhetorical_score,
        "narrative_score": log.narrative_score,
        "absence_score": log.absence_score
    }

# ==========================================================
# DASHBOARD HTML REAL (NUEVO)
# ==========================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, key: str, db: Session = Depends(get_db)):

    log = db.query(AnalysisLog).filter(
        AnalysisLog.analysis_key == key
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "analysis_key": log.analysis_key,
            "engine_version": log.engine_version,
            "level": log.level,
            "structural_index": log.risk_index,
            "trust_score": log.trust_score,
            "rhetorical_score": log.rhetorical_score,
            "narrative_score": log.narrative_score,
            "absence_score": log.absence_score
        }
    )

# ==========================================================
# PREMIUM JSON ENDPOINT
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
# REPORT ENDPOINT
# ==========================================================

@app.post("/v3/report")
async def generate_report(
    data: VerifyRequest,
    x_premium_token: str = Header(None)
):

    if not x_premium_token:
        raise HTTPException(status_code=401, detail="Acceso premium requerido")

    return {"status": "PDF endpoint activo"}