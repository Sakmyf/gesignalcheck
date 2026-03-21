# ======================================================
# SOURCE ANALYZER — ENGINE v8.7 COMPATIBLE
# ======================================================

from backend.domain_reputation import calculate_domain_score


KNOWN_MEDIA = [
    "clarin.com",
    "lanacion.com.ar",
    "infobae.com",
    "iprofesional.com"
]

LOW_QUALITY_PATTERNS = [
    ".xyz",
    ".click",
    ".top",
    "viral",
    "shocking",
    "increible"
]


def analyze_source(url: str):

    if not url:
        return {
            "domain": "",
            "score": 0,
            "signals": ["sin información de fuente"],
            "trust_level": 0.5,
            "type": "unknown"
        }

    u = url.lower()

    # --------------------------------------------------
    # BASE: DOMAIN REPUTATION
    # --------------------------------------------------
    domain_data = calculate_domain_score(url)

    trust_level = 0.6
    source_type = "generic"
    reason = "fuente no categorizada"

    # --------------------------------------------------
    # MEDIO CONOCIDO
    # --------------------------------------------------
    for domain in KNOWN_MEDIA:
        if domain in u:
            trust_level = 0.85
            source_type = "recognized_media"
            reason = "medio reconocido"
            break

    # --------------------------------------------------
    # DOMINIOS SOSPECHOSOS
    # --------------------------------------------------
    for pattern in LOW_QUALITY_PATTERNS:
        if pattern in u:
            trust_level = 0.3
            source_type = "low_quality"
            reason = "dominio de baja calidad"
            break

    # --------------------------------------------------
    # OUTPUT FINAL COMPATIBLE ENGINE
    # --------------------------------------------------
    return {
        "domain": domain_data.get("domain", ""),
        "score": domain_data.get("score", 0),
        "signals": domain_data.get("signals_positive", []) +
                   domain_data.get("signals_negative", []) +
                   [reason],
        "trust_level": trust_level,
        "type": source_type
    }