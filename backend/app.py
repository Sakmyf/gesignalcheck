from database import engine, Base, SessionLocal
import models

print("VERSION EXTENSION-ID ACTIVA - ESCALABLE METRICS")

import re
import uuid
import os
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import TableStyle


# ==========================================================
# CONFIG
# ==========================================================

ENGINE_VERSION = "v8.0"
LOGO_URL = "https://gesignalcheck.com/assets/logo.png"
LOGO_WIDTH_INCH = 1.2

ALLOWED_EXTENSIONS = [
    "fijnjbaacmpnhaaconoafbmnholbmaig"
]

app = FastAPI(title="GE SignalCheck API v8 - Scalable")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# ==========================================================
# MODEL INPUT
# ==========================================================

class VerifyRequest(BaseModel):
    url: str
    text: str

class EventRequest(BaseModel):
    event_name: str
    user_type: str = "free"


# ==========================================================
# SCORE FUNCTIONS
# ==========================================================

def map_score_to_level(score: float) -> str:
    if score <= 0.30:
        return "bajo"
    elif score <= 0.60:
        return "medio"
    return "alto"


def structural_score(url: str, text: str):
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")
    trust = 0.45
    signals = []

    if domain.endswith((".gov", ".edu", ".gob.ar", ".gov.ar")):
        trust = 0.85
        signals.append("Dominio institucional")

    if parsed.scheme == "https":
        trust += 0.05
        signals.append("HTTPS")

    if len(text.strip()) < 200:
        trust -= 0.05
        signals.append("Contenido limitado")

    return max(0, min(trust, 1)), signals


def rhetorical_score(text: str):
    score = 0
    signals = []
    upper = text.upper()

    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", upper):
        score += 0.25
        signals.append("Lenguaje alarmista")

    if re.search(r"\bCAOS\b|\bCOLAPSO\b", upper):
        score += 0.20
        signals.append("Carga emocional fuerte")

    return min(score, 1), signals


def narrative_score(text: str):
    score = 0
    signals = []
    lower = text.lower()

    if "según trascendió" in lower:
        score += 0.30
        signals.append("Narrativa no verificable")

    if "dijo" in lower and "http" not in lower:
        score += 0.20
        signals.append("Afirmaciones sin fuente visible")

    return min(score, 1), signals


def absence_of_source_score(text: str):
    score = 0
    signals = []

    if "http" not in text.lower():
        score += 0.25
        signals.append("No se detectan referencias a fuentes")

    return min(score, 1), signals


# ==========================================================
# ANALYSIS CORE
# ==========================================================

def collect_analysis(url, text):
    trust, s = structural_score(url, text)
    r, rs = rhetorical_score(text)
    n, ns = narrative_score(text)
    a, asg = absence_of_source_score(text)

    risk = (0.30*r)+(0.25*n)+(0.20*a)+(0.25*(1-trust))
    risk = max(0, min(risk, 1))

    return {
        "trust": trust,
        "r": r,
        "n": n,
        "a": a,
        "risk": risk,
        "signals": s + rs + ns + asg
    }


# ==========================================================
# METRICS LOGGER
# ==========================================================

def log_daily_metrics(risk_value, premium=False):
    db = SessionLocal()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    record = db.query(models.DailyMetrics).filter_by(date=today).first()

    if not record:
        record = models.DailyMetrics(
            date=today,
            total_verifications=1,
            total_premium_reports=1 if premium else 0,
            average_risk=risk_value
        )
        db.add(record)
    else:
        total = record.total_verifications + 1
        record.average_risk = ((record.average_risk * record.total_verifications) + risk_value) / total
        record.total_verifications = total
        if premium:
            record.total_premium_reports += 1

    db.commit()
    db.close()


# ==========================================================
# COUNTRY DETECTION (sin guardar IP)
# ==========================================================

def get_country_from_ip(ip: str) -> str:
    if not ip or ip in ["127.0.0.1", "::1"]:
        return "XX"
    try:
        response = requests.get(f"https://ipapi.co/{ip}/country_code/", timeout=2)
        if response.status_code == 200:
            country = response.text.strip().upper()
            return country if len(country) == 2 else "XX"
    except:
        pass
    return "XX"


# ==========================================================
# EVENT TRACKING
# ==========================================================

@app.post("/event")
async def log_event(event: EventRequest, request: Request):
    allowed_events = {
        "landing_view", "click_install", "verify_call", 
        "premium_request", "pdf_generated"
    }
    if event.event_name not in allowed_events:
        raise HTTPException(status_code=400, detail="Evento no permitido")
    
    if event.user_type not in ["free", "premium"]:
        event.user_type = "free"
    
    client_ip = request.client.host if request.client else "127.0.0.1"
    country = get_country_from_ip(client_ip)
    
    db = SessionLocal()
    try:
        new_event = models.AnonymousEvent(
            event_name=event.event_name,
            country=country,
            user_type=event.user_type
        )
        db.add(new_event)
        db.commit()
        return {"status": "logged"}
    finally:
        db.close()


# ==========================================================
# PDF GENERATOR
# ==========================================================

def fetch_logo():
    try:
        r = requests.get(LOGO_URL, timeout=5)
        path = "/tmp/logo.png"
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except:
        return None


def generate_pdf(data, url):
    file_id = str(uuid.uuid4())
    file_path = f"/tmp/report_{file_id}.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    logo = fetch_logo()
    if logo:
        img = Image(logo)
        img.drawWidth = LOGO_WIDTH_INCH * inch
        img.drawHeight = LOGO_WIDTH_INCH * inch
        img.hAlign = "CENTER"
        elements.append(img)
        elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("SignalCheck – Informe Estructural", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Fecha: {datetime.utcnow()}", styles["Normal"]))
    elements.append(Paragraph(f"Motor: {ENGINE_VERSION}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"URL: {url}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Índice estructural: {round(data['risk'],2)}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    return file_path


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():
    return {"status": "SignalCheck API v8 online"}


# ==========================================================
# VERIFY FREE
# ==========================================================

@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    ext = request.headers.get("x-extension-id")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    analysis = collect_analysis(data.url, data.text)
    log_daily_metrics(analysis["risk"], premium=False)

    return {
        "level": map_score_to_level(analysis["risk"]),
        "indicators": analysis["signals"][:5],
        "premium_available": True
    }


# ==========================================================
# PREMIUM PDF
# ==========================================================

@app.post("/v3/report")
async def report(request: Request, data: VerifyRequest, background_tasks: BackgroundTasks):

    token = request.headers.get("x-premium-token")
    if not token:
        raise HTTPException(status_code=401, detail="Acceso premium requerido")

    analysis = collect_analysis(data.url, data.text)
    log_daily_metrics(analysis["risk"], premium=True)

    file_path = generate_pdf(analysis, data.url)
    background_tasks.add_task(os.remove, file_path)

    return FileResponse(
        file_path,
        filename="signalcheck_informe.pdf",
        media_type="application/pdf"
    )


# ==========================================================
# METRICS ENDPOINTS
# ==========================================================

@app.get("/metrics/daily")
def get_daily_metrics():
    db = SessionLocal()
    data = db.query(models.DailyMetrics).all()
    db.close()
    return data


@app.get("/metrics/summary")
def metrics_summary():
    db = SessionLocal()
    total = db.query(models.DailyMetrics).count()
    db.close()
    return {"total_days_recorded": total}


@app.get("/metrics/internal")
def internal_metrics():
    db = SessionLocal()
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        by_event = db.query(
            models.AnonymousEvent.event_name,
            func.count(models.AnonymousEvent.id).label("count")
        ).filter(
            models.AnonymousEvent.timestamp >= week_ago
        ).group_by(models.AnonymousEvent.event_name).all()

        by_country = db.query(
            models.AnonymousEvent.country,
            func.count(models.AnonymousEvent.id).label("count")
        ).filter(
            models.AnonymousEvent.timestamp >= week_ago,
            models.AnonymousEvent.country != "XX"
        ).group_by(models.AnonymousEvent.country).all()

        total_verifies = db.query(func.count(models.AnonymousEvent.id)).filter(
            models.AnonymousEvent.event_name == "verify_call",
            models.AnonymousEvent.timestamp >= week_ago
        ).scalar()
        
        premium_requests = db.query(func.count(models.AnonymousEvent.id)).filter(
            models.AnonymousEvent.event_name == "premium_request",
            models.AnonymousEvent.timestamp >= week_ago
        ).scalar()

        conversion_rate = round((premium_requests / total_verifies * 100), 2) if total_verifies else 0

        return {
            "weekly_events": {e.event_name: e.count for e in by_event},
            "top_countries": {c.country: c.count for c in by_country},
            "conversion_rate_percent": conversion_rate,
            "total_weekly": sum(e.count for e in by_event)
        }
    finally:
        db.close()