import sys
import os
import re
import time
from datetime import datetime
from typing import List, Optional
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# Path fix
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ------------------------------------------------------------------------------
# ENV (Railway-safe)
# ------------------------------------------------------------------------------
load_dotenv()

ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8787,http://127.0.0.1:8787"
    ).split(",") if o.strip()
]

RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "2"))
RATE_WINDOW = 1.0
_rate_limit_buckets = defaultdict(lambda: deque())

# ------------------------------------------------------------------------------
# App
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Candado API",
    version="0.1.2-railway-stable"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Rate limit middleware (safe)
# ------------------------------------------------------------------------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = _rate_limit_buckets[ip]

        while bucket and bucket[0] <= now - RATE_WINDOW:
            bucket.popleft()

        if len(bucket) >= RATE_LIMIT_RPS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        bucket.append(now)
        return await call_next(request)

    except Exception:
        # Nunca crashear el proceso por middleware
        return await call_next(request)

# ------------------------------------------------------------------------------
# Models
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
# Regex signals
# ------------------------------------------------------------------------------
REGEX_TRUST = r'(?i)\b(cuit|cuil|raz[oó]n social|matr[ií]cula)\b'
REGEX_LEGAL = r'(?i)\b(t[eé]rminos|privacidad|legales|pol[ií]tica)\b'
REGEX_SPEC  = r'(?i)\b(podr[ií]a|ser[ií]a|rumor|trascendi[óo]|proyecta)\b'
REGEX_ALERT = r'(?i)\b(estafa|engaño|falso|fake|alerta|urgente)\b'
REGEX_MONEY = r'(?i)\b(deposit[aá]|transfer[ií]|cbu|cvu|alias)\b'

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def sanitize_for_privacy(text: str) -> str:
    text = re.sub(
        r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}',
        '[email]',
        text,
        flags=re.I
    )
    text = re.sub(r'\b\d{20,22}\b', '[cbu]', text)
    return text

# ------------------------------------------------------------------------------
# HTTP fetch (NO startup lifecycle, Railway-safe)
# ------------------------------------------------------------------------------
async def fetch_page_content(url: str) -> tuple[str, str]:
    try:
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "CandadoGuardian/1.0"}
        ) as client:
            r = await client.get(url)
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
# Rule engine
# ------------------------------------------------------------------------------
from rules.engine import analyze_text

def expert_rules_engine(text: str, url: str):
    score = 0
    reasons = []
    critical = False

    if re.search(REGEX_TRUST, text):
        score += 2
        reasons.append("Identidad verificable")

    if re.search(REGEX_LEGAL, text):
        score += 1
        reasons.append("Documentación legal")

    if url.startswith("https://"):
        score += 1
        reasons.append("HTTPS")

    if re.search(REGEX_SPEC, text):
        score -= 2
        reasons.append("Lenguaje especulativo")

    if re.search(REGEX_ALERT, text):
        score -= 2
        reasons.append("Lenguaje alarmista")

    if re.search(REGEX_MONEY, text) and not re.search(REGEX_LEGAL, text):
        score -= 5
        critical = True
        reasons.append("Solicitud de dinero sin respaldo legal")

    return score, reasons, critical

def interpret_score(score: int):
    if score >= 3:
        return "respaldado", 0.86
    if score >= 1:
        return "en_debate", 0.66
    if score >= 0:
        return "especulativo", 0.42
    return "contradicho", 0.22

# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "version": app.version}

@app.post("/v1/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest):
    text = req.text or ""

    if len(text) < 200:
        title, fetched = await fetch_page_content(req.url)
        if fetched:
            text = fetched
            req.title = req.title or title

    clean_text = sanitize_for_privacy(text)

    points, reasons, critical = expert_rules_engine(clean_text, req.url)

    if critical:
        label = "contradicho"
        base_score = 0.99
        method = "VETO_ETICO"
        summary = "Solicitud de dinero o datos sensibles sin respaldo legal."
    else:
        label, base_score = interpret_score(points)
        method = "expert_rules"
        summary = "Análisis por reglas."

    ai = analyze_text(clean_text)

    return VerifyResponse(
        label=label,
        score=min(base_score + ai.score, 1.0),
        summary=summary,
        evidence=reasons + ai.evidence,
        claims=[],
        method=f"{method} + rule_engine_v1",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=app.version
    )
