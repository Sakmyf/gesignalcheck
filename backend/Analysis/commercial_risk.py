## ======================================================
# SIGNALCHECK – COMMERCIAL RISK v2.1
# Detección de riesgo comercial / fraude contextual
# ======================================================

import re
from urllib.parse import urlparse

# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------

KNOWN_DOMAINS = [
    "mercadolibre",
    "amazon",
    "ebay",
    "fravega",
    "garbarino",
    "carrefour",
    "coto",
    "vecompras",
    "tececompras",
]

HIGH_VALUE_PRODUCTS = [
    "iphone",
    "samsung",
    "macbook",
    "notebook",
    "playstation",
]

LOGIN_PATTERNS = [
    "iniciar sesión",
    "registrate",
    "crear cuenta",
    "acceder",
    "ver precios",
]

PRICE_HIDDEN_PATTERNS = [
    "ver precio",
    "consultar precio",
    "precio no disponible",
]

GENERIC_REVIEWS_PATTERNS = [
    r"\d{3,} reviews",
    r"\d{3,} opiniones",
    r"\d{1,3},\d{3}",
]

LEGAL_PATTERNS = [
    "cuit",
    "razón social",
    "direccion",
    "términos",
    "condiciones",
]

SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".click", ".site", ".store", ".online"
]

PAYMENT_PRESSURE_PATTERNS = [
    r"\bdepositá\b", r"\btransferí\b",
    r"\bcbu\b", r"\bcvu\b",
    r"\bclave token\b", r"\benviar dinero\b",
    r"\bpago anticipado\b",
]

# ------------------------------------------------------
# UTIL
# ------------------------------------------------------

def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""


def is_ecommerce_context(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ["comprar", "carrito", "oferta", "envío"])


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------

def analyze_commercial_risk(text: str, url: str = "") -> dict:

    text_lower = text.lower()
    domain = extract_domain(url)

    risk_score = 0
    signals = []

    # --------------------------------------------------
    # 1. CONTEXTO
    # --------------------------------------------------

    if not is_ecommerce_context(text):
        return {
            "level": "none",
            "score": 0,
            "summary": "",
            "signals": []
        }

    # --------------------------------------------------
    # 2. DOMINIO DESCONOCIDO + TLD SOSPECHOSO
    # --------------------------------------------------

    if domain and not any(k in domain for k in KNOWN_DOMAINS):
        risk_score += 4
        signals.append("Dominio no reconocido o de baja reputación")

    if domain and any(tld in domain for tld in SUSPICIOUS_TLDS):
        risk_score += 3
        signals.append("TLD asociado a sitios de alto riesgo")

    # --------------------------------------------------
    # 3. LOGIN / BLOQUEO
    # --------------------------------------------------

    if any(p in text_lower for p in LOGIN_PATTERNS):
        risk_score += 3
        signals.append("Acceso restringido o login obligatorio")

    # --------------------------------------------------
    # 4. PRECIO OCULTO
    # --------------------------------------------------

    if any(p in text_lower for p in PRICE_HIDDEN_PATTERNS):
        risk_score += 2
        signals.append("Información de precios no visible")

    # --------------------------------------------------
    # 5. PRODUCTO ALTO VALOR
    # --------------------------------------------------

    if any(p in text_lower for p in HIGH_VALUE_PRODUCTS):
        risk_score += 2
        signals.append("Producto de alto valor detectado")

    # --------------------------------------------------
    # 6. REVIEWS SOSPECHOSAS
    # --------------------------------------------------

    for pattern in GENERIC_REVIEWS_PATTERNS:
        if re.search(pattern, text_lower):
            risk_score += 3
            signals.append("Patrones de reseñas potencialmente artificiales")
            break

    # --------------------------------------------------
    # 7. FALTA INFO LEGAL
    # --------------------------------------------------

    if not any(k in text_lower for k in LEGAL_PATTERNS):
        risk_score += 2
        signals.append("Ausencia de información legal identificable")

    # --------------------------------------------------
    # 8. PRESIÓN DE PAGO / DATOS SENSIBLES
    # --------------------------------------------------

    if any(re.search(p, text_lower) for p in PAYMENT_PRESSURE_PATTERNS):
        risk_score += 4
        signals.append("Solicitud de transferencia o datos sensibles")

    # --------------------------------------------------
    # 9. NORMALIZACIÓN (ANTI FALSO POSITIVO)
    # --------------------------------------------------

    # Si el dominio es conocido, reducimos riesgo
    if domain and any(k in domain for k in KNOWN_DOMAINS):
        risk_score *= 0.5

    # Limitar score
    risk_score = min(risk_score, 10)

    # --------------------------------------------------
    # LEVEL
    # --------------------------------------------------

    if risk_score >= 7:
        level = "alto"
    elif risk_score >= 4:
        level = "medio"
    else:
        level = "bajo"

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    if level == "alto":
        summary = "El sitio presenta múltiples señales de riesgo comercial."
    elif level == "medio":
        summary = "Se detectan indicadores que sugieren cautela en la compra."
    else:
        summary = "No se detectan señales relevantes de riesgo comercial."

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------

    return {
        "level": level,
        "score": round(risk_score, 1),
        "summary": summary,
        "signals": signals[:5]
    }