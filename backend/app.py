print("VERSION EXTENSION-ID ACTIVA")

import re
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# ---------------------------------------
# FASTAPI INIT
# ---------------------------------------
app = FastAPI(title="GE SignalCheck API v6 - Extension Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------
# EXTENSIONES AUTORIZADAS
# ---------------------------------------
ALLOWED_EXTENSIONS = [
    "fijnjbaacmpnhaaconoafbmnholbmaig"
]


# ---------------------------------------
# MODELO DE ENTRADA
# ---------------------------------------
class VerifyRequest(BaseModel):
    url: str
    text: str = ""


# ---------------------------------------
# SCORE ESTRUCTURAL
# ---------------------------------------
def structural_score(url: str, text: str):

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # eliminar www.
    if domain.startswith("www."):
        domain = domain[4:]

    signals = []
    domain_type = "unknown"

    # --- Categorías de dominio ---
    INSTITUTIONAL = [".gov", ".gov.ar", ".gob.ar", ".edu", ".edu.ar"]

    TRADITIONAL_MEDIA = {
        "reuters.com",
        "bbc.com",
        "lanacion.com.ar",
        "clarin.com",
        "chequeado.com",
        "iprofesional.com"
    }

    SATIRICAL_SITES = {
        "elmundo.today",
        "theonion.com",
        "clickhole.com"
    }

    SOCIAL_MEDIA = {
        "facebook.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "tiktok.com"
    }

    SHORTENERS = {
        "bit.ly",
        "tinyurl.com"
    }

    trust = 0.45  # Base neutral

    # --- Clasificación estructural ---
    if any(domain.endswith(tld) for tld in INSTITUTIONAL):
        trust = 0.85
        domain_type = "institutional"
        signals.append("Dominio institucional")

    elif domain in TRADITIONAL_MEDIA:
        trust = 0.70
        domain_type = "traditional_media"
        signals.append("Medio tradicional")

    elif domain in SATIRICAL_SITES:
        trust = 0.50
        domain_type = "satire"
        signals.append("Sitio satírico declarado")

    elif domain in SOCIAL_MEDIA:
        trust = 0.40
        domain_type = "social"
        signals.append("Contenido en red social")

    elif domain in SHORTENERS:
        trust = 0.25
        domain_type = "shortener"
        signals.append("Dominio acortador")

    # --- HTTPS ---
    if parsed.scheme == "https":
        trust += 0.05
        signals.append("HTTPS")

    # --- Texto demasiado corto ---
    if len(text.strip()) < 200:
        trust -= 0.05
        signals.append("Contenido limitado")

    trust = max(0.0, min(trust, 1.0))

    return trust, signals, domain_type

# ---------------------------------------
# SCORE RETÓRICO
# ---------------------------------------
def rhetorical_score(text: str, domain_type: str):

    score = 0.0
    signals = []

    upper = text.upper()
    lower = text.lower()

    # ---------------------------------------
    # 1️⃣ Alarmismo explícito
    # ---------------------------------------
    if re.search(r"\bURGENTE\b|\bESCÁNDALO\b|\bIMPACTANTE\b", upper):
        score += 0.25
        signals.append("Lenguaje alarmista")

    # ---------------------------------------
    # 2️⃣ Carga emocional fuerte
    # ---------------------------------------
    if re.search(r"\bCAOS\b|\bCOLAPSO\b|\bTRAICIÓN\b", upper):
        score += 0.20
        signals.append("Carga emocional fuerte")

    # ---------------------------------------
    # 3️⃣ MAYÚSCULAS INTELIGENTES (v3)
    # ---------------------------------------

    # No penalizar medios tradicionales ni institucionales
    if domain_type not in ["institutional", "traditional_media"]:

        if len(text) > 400:

            letters = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", text)
            upper_letters = re.findall(r"[A-ZÁÉÍÓÚÑ]", text)

            if len(letters) > 0:
                upper_ratio = len(upper_letters) / len(letters)
            else:
                upper_ratio = 0

            if upper_ratio > 0.40:
                score += 0.15
                signals.append("Uso excesivo de mayúsculas (tono enfático)")

            elif upper_ratio > 0.30:
                score += 0.08
                signals.append("Uso marcado de mayúsculas")

    return min(score, 1.0), signals

    # ---------------------------------------
# MAYÚSCULAS INTELIGENTES v3
# ---------------------------------------

def uppercase_score(text: str, domain_type: str):

    score = 0.0
    signals = []

    # No penalizar medios tradicionales ni institucionales
    if domain_type in ["institutional", "traditional_media"]:
        return 0.0, signals

    if len(text) < 400:
        return 0.0, signals

    letters = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", text)
    upper_letters = re.findall(r"[A-ZÁÉÍÓÚÑ]", text)

    if len(letters) == 0:
        return 0.0, signals

    upper_ratio = len(upper_letters) / len(letters)

    # Solo penalizar si es realmente exagerado
    if upper_ratio > 0.40:
        score += 0.15
        signals.append("Uso excesivo de mayúsculas (tono enfático)")
    elif upper_ratio > 0.30:
        score += 0.08
        signals.append("Uso marcado de mayúsculas")

    return score, signals

# ---------------------------------------
# MAYÚSCULAS CONTEXTUALES (v3)
# Solo analiza bloques largos de texto narrativo
# ---------------------------------------

paragraphs = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ\s]{80,}", text)

uppercase_blocks = 0

for p in paragraphs:
    letters = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", p)
    upper_letters = re.findall(r"[A-ZÁÉÍÓÚÑ]", p)

    if len(letters) == 0:
        continue

    upper_ratio = len(upper_letters) / len(letters)

    # Solo contar si el bloque narrativo tiene exceso real
    if upper_ratio > 0.40:
        uppercase_blocks += 1

if uppercase_blocks >= 1:
    score += 0.12
    signals.append("Uso enfático de mayúsculas en contenido narrativo")


# ---------------------------------------
# SCORE NARRATIVO
# ---------------------------------------
def narrative_score(text: str, domain_type: str):

    score = 0.0
    signals = []
    lower = text.lower()

    # 🚫 Si es sitio satírico, no penalizamos narrativa
    if domain_type == "satire":
        return 0.0, []

    # Relato recreado o imaginado
    if re.search(
        r"\bescena imaginada\b|\brecreación\b|\bsegún trascendió\b|\bdentro de este relato\b",
        lower
    ):
        score += 0.30
        signals.append("Narrativa no verificable")

    # Dramatización exagerada
    if re.search(
        r"\bdejó paralizada\b|\bdejó en silencio\b|\bola imparable\b|\bel país entero\b",
        lower
    ):
        score += 0.25
        signals.append("Dramatización narrativa")

    # Declaraciones sin fuente visible
    if re.search(r"\bdijo\b|\bafirmó\b|\bdeclaró\b", lower):
        if "http" not in lower and "www." not in lower:
            score += 0.20
            signals.append("Afirmaciones sin fuente visible")

    return min(score, 1.0), signals

# ---------------------------------------
# AUSENCIA DE FUENTE
# ---------------------------------------
def absence_of_source_score(text: str):

    score = 0.0
    signals = []
    lower = text.lower()

    has_link = bool(re.search(r"http[s]?://|www\.", lower))
    has_reference = bool(re.search(r"\bsegún\b|\bde acuerdo con\b|\bfuente\b", lower))

    if not has_link and not has_reference:
        score += 0.25
        signals.append("No se detectan referencias a fuentes")

    return min(score, 1.0), signals


# ---------------------------------------
# ROOT
# ---------------------------------------
@app.get("/")
def root():
    return {"status": "GE SignalCheck API online"}


# ---------------------------------------
# ENDPOINT PRINCIPAL
# ---------------------------------------
@app.post("/v3/verify")
async def verify(request: Request, data: VerifyRequest):

    extension_id = request.headers.get("x-extension-id")

    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no identificada")

    if extension_id.strip() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=403, detail="Extensión no autorizada")

    if not data.text or len(data.text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Texto insuficiente")

    trust_score, s_signals, domain_type = structural_score(data.url, data.text)
    r_score, r_signals = rhetorical_score(data.text, domain_type)
    n_score, n_signals = narrative_score(data.text)
    a_score, a_signals = absence_of_source_score(data.text)

    # ---------------------------------------
    # FÓRMULA PROFESIONAL EQUILIBRADA
    # ---------------------------------------
    risk_index = (
        (0.30 * r_score) +
        (0.25 * n_score) +
        (0.20 * a_score) +
        (0.25 * (1 - trust_score))
    )

    # Ajuste por tipo de dominio
    if domain_type == "traditional_media":
        risk_index *= 0.85

    if domain_type == "social":
        risk_index = max(risk_index, 0.35)

    risk_index = max(0.0, min(risk_index, 1.0))

    # ---------------------------------------
    # CONTEXT WARNING
    # ---------------------------------------
    context_warning = None

    if n_score >= 0.4:
        context_warning = "Posible relato ficcional presentado como hecho real"
    elif a_score >= 0.3:
        context_warning = "Contenido sin referencias externas visibles"
    elif r_score >= 0.4:
        context_warning = "Lenguaje emocional o dramatizado"

    return {
        "structural_trust_score": round(trust_score, 2),
        "source_type": domain_type,
        "rhetorical_manipulation_score": round(r_score, 2),
        "narrative_risk_score": round(n_score, 2),
        "absence_of_source_score": round(a_score, 2),
        "risk_index": round(risk_index, 2),
        "context_warning": context_warning,
        "details": {
            "structural_signals": s_signals,
            "rhetorical_signals": r_signals,
            "narrative_signals": n_signals,
            "source_signals": a_signals
        }
    }
