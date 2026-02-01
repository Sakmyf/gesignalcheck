# ==============================================================================
# CANDADO API - THE GUARDIAN (v0.1.2 - Intermedio)
# ==============================================================================

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from collections import defaultdict, deque
import os
import re
import time

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# .env
# ------------------------------------------------------------------------------
load_dotenv()

ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8787,http://localhost:8787"
    ).split(",") if o.strip()
]

RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "2"))
RATE_WINDOW = 1.0  # segundos
_rate_limit_buckets = defaultdict(lambda: deque())

# ------------------------------------------------------------------------------
# App
# ------------------------------------------------------------------------------
app = FastAPI(title="Candado API", version="0.1.2-guardian-intermedio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Rate Limit Middleware (por IP) – CORRECTO (sin 500)
# ------------------------------------------------------------------------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    bucket = _rate_limit_buckets[client_ip]

    while bucket and bucket[0] <= now - RATE_WINDOW:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_RPS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    bucket.append(now)
    return await call_next(request)

# ------------------------------------------------------------------------------
# Modelos
# ------------------------------------------------------------------------------
class Claim(BaseModel):
    text: str
    label: str
    evidence_strength: str
    risk_if_wrong: str

class VerifyRequest(BaseModel):
    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    locale: Optional[str] = "es-AR"

class VerifyResponse(BaseModel):
    label: str
    score: float
    summary: str
    evidence: List[str]
    claims: List[Claim]
    method: str
    timestamp: str
    version: str

# ------------------------------------------------------------------------------
# Regex / Señales
# ------------------------------------------------------------------------------
REGEX_TRUST = r'(?i)\b(cuit|cuil|raz[oó]n social|matr[ií]cula)\b'
REGEX_LEGAL = r'(?i)\b(t[eé]rminos|privacidad|legales|pol[ií]tica)\b'
REGEX_EVENT = r'(?i)\b(fecha|lugar|cronograma|se realizar[áa]|tendr[áa] lugar|entrada (libre|gratis))\b'
REGEX_SPEC  = r'(?i)\b(podr[ií]a|ser[ií]a|estar[ií]a por|rumor|trascendi[óo]|proyecta)\b'
REGEX_ALERT = r'(?i)\b(estafa|engaño|falso|fake|alerta|urgente)\b'
REGEX_MONEY = r'(?i)\b(deposit[aá]|transfer[ií]|cbu|cvu|alias)\b'

WHITELIST_OK = ["chequeado", "gob", "boletin", "who.int", "un.org"]

SAFE_GREEN_MIN = 3
DEBATE_MIN = 1

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def sanitize_for_privacy(txt: str) -> str:
    txt = re.sub(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', '[email]', txt, flags=re.I)
    txt = re.sub(r'\b\d{20,22}\b', '[cbu]', txt)
    return txt

# ------------------------------------------------------------------------------
# HTTP Client
# ------------------------------------------------------------------------------
http_client = httpx.AsyncClient(
    timeout=10.0,
    follow_redirects=True,
    headers={"User-Agent": "CandadoGuardian/1.0"}
)

@app.on_event("shutdown")
async def shutdown():
    await http_client.aclose()

async def fetch_page_content(url: str) -> tuple[str, str]:
    try:
        r = await http_client.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        body = soup.body or soup

        for tag in body(["script", "style", "nav", "footer", "header", "aside", "img"]):
            tag.decompose()

        text = body.get_text(" ", strip=True)[:15000]
        return title, text
    except Exception:
        return "", ""

# ------------------------------------------------------------------------------
# Motor de reglas
# ------------------------------------------------------------------------------
def expert_rules_engine(text: str, url: str):
    score = 0
    detected = []
    is_critical = False

    if re.search(REGEX_TRUST, text):
        score += 2
        detected.append("Identidad verificable")

    if re.search(REGEX_LEGAL, text):
        score += 1
        detected.append("Documentación legal")

    if "https://" in url:
        score += 1
        detected.append("HTTPS")

    if re.search(REGEX_SPEC, text):
        score -= 2
        detected.append("Lenguaje especulativo")

    if re.search(REGEX_ALERT, text):
        score -= 2
        detected.append("Lenguaje de alerta")

    if re.search(REGEX_MONEY, text) and not re.search(REGEX_LEGAL, text):
        score -= 5
        is_critical = True
        detected.append("Solicitud de dinero sin respaldo legal")

    return score, detected, is_critical

def interpret_score(pts: int):
    if pts >= SAFE_GREEN_MIN:
        return "respaldado", 0.86
    if pts >= DEBATE_MIN:
        return "en_debate", 0.66
    if pts >= 0:
        return "especulativo", 0.42
    return "contradicho", 0.22

# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}

@app.post("/v1/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest, background_tasks: BackgroundTasks):
    t0 = time.time()
    text = req.text or ""

    if len(text) < 200 and req.url:
        title, fetched = await fetch_page_content(req.url)
        if len(fetched) > 200:
            text = fetched
            if not req.title:
                req.title = title

    clean_text = sanitize_for_privacy(text)

    points, reasons, is_critical = expert_rules_engine(clean_text, req.url)

    if is_critical:
        label = "contradicho"
        score = 0.99
        method = "VETO_ETICO"
        summary = "Solicitud de dinero o datos sensibles sin respaldo legal."
    else:
        label, score = interpret_score(points)
        method = "expert_rules"
        summary = "Análisis por reglas."

    return VerifyResponse(
        label=label,
        score=score,
        summary=summary,
        evidence=reasons,
        claims=[],
        method=method,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=app.version
    )

