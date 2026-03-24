# ======================================================
# SOURCE ANALYZER — EXPANDED COVERAGE
# FIX P0: reemplaza substring matching ("who.int" in url)
# por comparación correcta de hostname con urlparse.
# Antes: "who.int" in "fake-who.int.evil.com" → True (spoofable)
# Ahora: hostname == "who.int" or hostname.endswith(".who.int") → False ✓
# ======================================================

from urllib.parse import urlparse


def _extract_hostname(url: str) -> str:
    """Extrae el hostname real de una URL, tolerando URLs sin esquema."""
    raw = url if url.startswith("http") else "https://" + url
    try:
        return urlparse(raw.lower()).hostname or ""
    except Exception:
        return ""


def _match(hostname: str, pattern: str) -> bool:
    """
    Compara el hostname contra un patrón de dominio.
    - Patrón con punto inicial (".edu", ".click"): chequea TLD exacto.
    - Patrón normal ("who.int"): chequea hostname exacto o subdominio.
    """
    if pattern.startswith("."):
        # TLD pattern: hostname debe terminar con ".edu", ".click", etc.
        return hostname.endswith(pattern)
    else:
        # Dominio exacto o subdominio legítimo (news.bbc.com → bbc.com)
        return hostname == pattern or hostname.endswith("." + pattern)


def analyze_source(url: str):

    if not url:
        return {
            "domain": "",
            "trust_level": 0.5,
            "type": "unknown",
            "signals": ["sin información de fuente"]
        }

    hostname = _extract_hostname(url)

    if not hostname:
        return {
            "domain": "",
            "trust_level": 0.5,
            "type": "unknown",
            "signals": ["url no parseable"]
        }

    # --------------------------------------------------
    # 🟢 ALTA CONFIANZA (0.92)
    # --------------------------------------------------
    high_trust = [
        "argentina.gob.ar", "gov.ar", "gob.ar",
        "who.int", "un.org", "unesco.org", "paho.org",
        "worldbank.org", "imf.org", "oas.org",
        "vatican.va",
        ".edu.ar", ".edu",
        "chequeado.com", "snopes.com", "factcheck.org",
        "fullfact.org", "politifact.com",
    ]

    # --------------------------------------------------
    # 🟡 CONFIANZA MEDIA-ALTA (0.72)
    # --------------------------------------------------
    medium_high_trust = [
        "clarin.com", "lanacion.com.ar", "infobae.com",
        "pagina12.com.ar", "cronista.com", "ambito.com",
        "telam.com.ar", "perfil.com",
        "bbc.com", "reuters.com", "apnews.com",
        "theguardian.com", "elpais.com", "elmundo.es",
        "nytimes.com", "washingtonpost.com",
        "dw.com", "france24.com",
        "eluniversal.com", "eltiempo.com", "folha.uol.com.br",
    ]

    # --------------------------------------------------
    # 🟡 CONFIANZA MEDIA (0.60)
    # --------------------------------------------------
    medium_trust = [
        "mercadolibre.com", "amazon.com", "garbarino.com.ar",
        "fravega.com", "musimundo.com",
        "youtube.com", "twitter.com", "x.com",
        "linkedin.com", "facebook.com",
        "cronica.com.ar", "minutouno.com", "eldestape.com.ar",
    ]

    # --------------------------------------------------
    # 🔴 BAJA CONFIANZA (0.25)
    # FIX: "t.co/" → "t.co" (el slash no es parte del hostname)
    # --------------------------------------------------
    low_trust = [
        ".click", ".xyz", ".top", ".tk", ".ml", ".ga", ".cf",
        "bit.ly", "tinyurl.com", "t.co",
    ]

    # --------------------------------------------------
    # MATCH — orden importa (más específico primero)
    # --------------------------------------------------

    for d in high_trust:
        if _match(hostname, d):
            return {
                "domain": hostname,
                "trust_level": 0.92,
                "type": "high_trust",
                "signals": ["fuente institucional o verificadora confiable"]
            }

    for d in medium_high_trust:
        if _match(hostname, d):
            return {
                "domain": hostname,
                "trust_level": 0.72,
                "type": "medium_high_trust",
                "signals": ["medio de comunicación establecido"]
            }

    for d in medium_trust:
        if _match(hostname, d):
            return {
                "domain": hostname,
                "trust_level": 0.60,
                "type": "medium_trust",
                "signals": ["fuente conocida, contexto variable"]
            }

    for d in low_trust:
        if _match(hostname, d):
            return {
                "domain": hostname,
                "trust_level": 0.25,
                "type": "low_trust",
                "signals": ["dominio o acortador de baja confianza"]
            }

    return {
        "domain": hostname,
        "trust_level": 0.55,
        "type": "neutral",
        "signals": []
    }
