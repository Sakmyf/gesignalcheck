# ======================================================
# SIGNALCHECK – COMMERCIAL RISK MODULE
# Detecta señales de posible fraude en sitios comerciales
# ======================================================

import re
from urllib.parse import urlparse

# ------------------------------------------------------
# CONFIGURACIÓN BASE
# ------------------------------------------------------

SUSPICIOUS_KEYWORDS = [
    "oferta exclusiva",
    "solo hoy",
    "descuento limitado",
    "últimas unidades",
    "compra ahora",
]

GENERIC_REVIEWS_PATTERNS = [
    r"\d{3,} reviews",
    r"\d{3,} opiniones",
    r"\d{1,3},\d{3}",
]

KNOWN_DOMAINS = [
    "mercadolibre",
    "amazon",
    "ebay",
    "fravega",
    "garbarino",
    "compraahora",
    "carrefour",
]

HIGH_VALUE_PRODUCTS = [
    "iphone",
    "samsung",
    "macbook",
    "notebook",
]

# ------------------------------------------------------
# UTILIDAD
# ------------------------------------------------------

def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""

# ------------------------------------------------------
# DETECTOR PRINCIPAL
# ------------------------------------------------------

def analyze_commercial_risk(text: str, url: str = "") -> dict:

    risk_score = 0
    signals = []

    text_lower = text.lower()
    domain = extract_domain(url)

    # --------------------------------------------------
    # 1. Dominio sospechoso
    # --------------------------------------------------
    if domain:
        if not any(k in domain for k in KNOWN_DOMAINS):
            risk_score += 3
            signals.append("Dominio no reconocido o poco habitual")

    # --------------------------------------------------
    # 2. Producto de alto valor + contexto comercial
    # --------------------------------------------------
    if any(p in text_lower for p in HIGH_VALUE_PRODUCTS):
        risk_score += 2
        signals.append("Producto de alto valor detectado")

    # --------------------------------------------------
    # 3. Patrones de reviews genéricas
    # --------------------------------------------------
    for pattern in GENERIC_REVIEWS_PATTERNS:
        if re.search(pattern, text_lower):
            risk_score += 3
            signals.append("Patrones de reseñas potencialmente artificiales")
            break

    # --------------------------------------------------
    # 4. Palabras comerciales agresivas
    # --------------------------------------------------
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in text_lower:
            risk_score += 2
            signals.append("Lenguaje comercial agresivo detectado")
            break

    # --------------------------------------------------
    # 5. Falta de información legal básica
    # --------------------------------------------------
    if not any(k in text_lower for k in ["cuit", "razón social", "direccion", "términos"]):
        risk_score += 2
        signals.append("Ausencia de información legal identificable")

    # --------------------------------------------------
    # NIVEL FINAL
    # --------------------------------------------------
    if risk_score >= 8:
        level = "alto"
    elif risk_score >= 4:
        level = "medio"
    else:
        level = "bajo"

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------
    return {
        "level": level,
        "score": risk_score,
        "summary": build_summary(level),
        "signals": signals
    }


# ------------------------------------------------------
# RESUMEN AUTOMÁTICO
# ------------------------------------------------------

def build_summary(level: str) -> str:
    if level == "alto":
        return "El sitio presenta múltiples señales de posible riesgo comercial."
    elif level == "medio":
        return "Se detectaron algunos indicadores que podrían sugerir riesgo comercial."
    else:
        return "No se detectan señales relevantes de riesgo comercial."