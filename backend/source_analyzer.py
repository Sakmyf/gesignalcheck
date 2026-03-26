# ======================================================
# SOURCE ANALYZER v3.0
# Clasificación por tipo de fuente, no por lista de dominios.
# Principio: el desconocido no es sospechoso,
# la red social requiere más atención,
# lo comercial es explícitamente persuasivo.
# ======================================================

from urllib.parse import urlparse
import re


def _extract_hostname(url: str) -> str:
    raw = url if url.startswith("http") else "https://" + url
    try:
        return urlparse(raw.lower()).hostname or ""
    except Exception:
        return ""


def _detect_source_type(hostname: str) -> str:
    """
    Clasifica el tipo de fuente por TLD y patrones de dominio.
    No usa listas de medios — usa características estructurales del dominio.
    """

    # --------------------------------------------------
    # INSTITUCIONAL
    # TLDs gubernamentales, académicos, organismos internacionales
    # --------------------------------------------------
    institutional_tlds = [
        ".gov", ".gob", ".gov.ar", ".gob.ar", ".gov.mx", ".gob.mx",
        ".gov.co", ".gob.cl", ".gov.br", ".gov.py", ".gov.uy",
        ".gov.pe", ".gov.ec", ".gov.ve", ".gov.bo",
        ".edu", ".edu.ar", ".edu.mx", ".edu.co", ".edu.pe",
        ".edu.br", ".edu.uy", ".edu.cl", ".edu.es",
        ".int", ".org.ar",
    ]

    institutional_exact = [
        "who.int", "un.org", "unesco.org", "paho.org",
        "worldbank.org", "imf.org", "oas.org", "vatican.va",
        "cepal.org", "eclac.org",
        "chequeado.com", "snopes.com", "factcheck.org",
        "fullfact.org", "politifact.com", "maldita.es",
        "lupa.news", "agencialupa.com",
    ]

    for tld in institutional_tlds:
        if hostname.endswith(tld):
            return "institutional"

    for domain in institutional_exact:
        if hostname == domain or hostname.endswith("." + domain):
            return "institutional"

    # --------------------------------------------------
    # RED SOCIAL
    # Sin proceso editorial, sin verificación, alta viralidad
    # --------------------------------------------------
    social_domains = [
        "facebook.com", "fb.com",
        "twitter.com", "x.com",
        "instagram.com",
        "tiktok.com",
        "youtube.com",
        "t.me", "telegram.org",
        "reddit.com",
        "threads.net",
        "whatsapp.com",
    ]

    for domain in social_domains:
        if hostname == domain or hostname.endswith("." + domain):
            return "social"

    # --------------------------------------------------
    # COMERCIAL
    # Ecommerce establecido — persuasión explícita esperada
    # --------------------------------------------------
    commercial_domains = [
        "mercadolibre.com", "mercadopago.com",
        "amazon.com", "amazon.com.br", "amazon.com.mx",
        "ebay.com", "aliexpress.com",
        "falabella.com", "ripley.com", "linio.com",
        "garbarino.com.ar", "fravega.com", "musimundo.com",
        "tiendamia.com", "letsbit.com",
    ]

    for domain in commercial_domains:
        if hostname == domain or hostname.endswith("." + domain):
            return "commercial"

    # --------------------------------------------------
    # TLD SOSPECHOSO
    # Dominios usados frecuentemente para spam/phishing
    # --------------------------------------------------
    suspicious_tlds = [
        ".xyz", ".click", ".top", ".tk", ".ml",
        ".ga", ".cf", ".buzz", ".icu", ".monster",
    ]

    for tld in suspicious_tlds:
        if hostname.endswith(tld):
            return "suspicious"

    # --------------------------------------------------
    # ACORTADORES
    # --------------------------------------------------
    shorteners = ["bit.ly", "tinyurl.com", "t.co", "ow.ly", "buff.ly"]
    for s in shorteners:
        if hostname == s or hostname.endswith("." + s):
            return "suspicious"

    # --------------------------------------------------
    # DEFAULT → desconocido (neutro, no sospechoso)
    # --------------------------------------------------
    return "unknown"


def _detect_media_signals(text: str) -> bool:
    """
    Detecta si el contenido tiene estructura periodística,
    independientemente del dominio.
    No da confianza extra — solo contextualiza labels.
    """
    if not text:
        return False

    t = text.lower()
    signals = 0

    # Verbos de reporte
    report_verbs = [
        r"\bdeclaró\b", r"\binformó\b", r"\bsegún\b",
        r"\breportó\b", r"\bafirmó\b", r"\bseñaló\b",
        r"\bconfirmó\b", r"\bindicó\b", r"\baseguró\b",
        r"\bde acuerdo con\b",
    ]
    if sum(1 for p in report_verbs if re.search(p, t)) >= 2:
        signals += 1

    # Byline / firma
    if re.search(r"\bpor\s+[A-ZÁÉÍÓÚ][a-záéíóú]+\b", text):
        signals += 1

    # Fecha de publicación
    if re.search(r"\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b", t):
        signals += 1

    # Estructura de sección
    if re.search(r"\b(política|economía|sociedad|deportes|internacional|cultura|tecnología|salud|judiciales)\b", t):
        signals += 1

    # Citas textuales
    if text.count('"') >= 2 or text.count('«') >= 1:
        signals += 1

    return signals >= 3


# ======================================================
# FUNCIÓN PRINCIPAL
# ======================================================

SOURCE_CONFIG = {
    "institutional": {
        "trust_level": 0.90,
        "label": "institutional",
        "message": "Fuente institucional verificable",
        "signals": ["fuente institucional verificable"],
    },
    "media": {
        "trust_level": 0.65,
        "label": "media",
        "message": "Contenido periodístico — puede tener sesgo editorial",
        "signals": ["medio periodístico detectado"],
    },
    "commercial": {
        "trust_level": 0.55,
        "label": "commercial",
        "message": "Contenido comercial — orientado a persuadir la compra",
        "signals": ["contenido comercial — persuasión esperada"],
    },
    "unknown": {
        "trust_level": 0.55,
        "label": "unknown",
        "message": "Fuente no categorizada — leé con atención",
        "signals": [],
    },
    "social": {
        "trust_level": 0.30,
        "label": "social",
        "message": "Contenido en red social — sin verificación editorial",
        "signals": ["red social — sin proceso editorial"],
    },
    "suspicious": {
        "trust_level": 0.15,
        "label": "suspicious",
        "message": "Dominio de baja confianza — alto escrutinio recomendado",
        "signals": ["dominio o acortador de baja confianza"],
    },
}


def analyze_source(url: str, text: str = "") -> dict:

    if not url:
        return {
            "domain":      "",
            "trust_level": 0.55,
            "type":        "unknown",
            "label":       "unknown",
            "message":     "Sin información de fuente",
            "signals":     [],
        }

    hostname = _extract_hostname(url)

    if not hostname:
        return {
            "domain":      "",
            "trust_level": 0.55,
            "type":        "unknown",
            "label":       "unknown",
            "message":     "URL no parseable",
            "signals":     [],
        }

    source_type = _detect_source_type(hostname)

    # Si el dominio es desconocido pero el texto tiene
    # estructura periodística → clasificar como medio
    if source_type == "unknown" and text and _detect_media_signals(text):
        source_type = "media"

    config = SOURCE_CONFIG[source_type]

    return {
        "domain":      hostname,
        "trust_level": config["trust_level"],
        "type":        source_type,
        "label":       config["label"],
        "message":     config["message"],
        "signals":     config["signals"],
    }