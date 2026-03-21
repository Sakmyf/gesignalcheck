# ======================================================
# SIGNALCHECK – SOURCE ANALYZER v1.0
# Evalúa la confiabilidad de la fuente (no el contenido)
# ======================================================

KNOWN_MEDIA = [
    "nytimes.com",
    "bbc.com",
    "cnn.com",
    "reuters.com",
    "theguardian.com",
    "infobae.com",
    "clarin.com",
    "lanacion.com.ar",
    "pagina12.com.ar"
]

LOW_QUALITY_PATTERNS = [
    "blogspot",
    "wordpress",
    "noticias-24",
    "viral",
    "alerta",
    "secreto"
]


def analyze_source(url: str):
    """
    Analiza la fuente del contenido
    """

    if not url:
        return {
            "trust_level": 0.5,
            "type": "unknown",
            "reason": "sin información de fuente"
        }

    u = url.lower()

    # --------------------------------------------------
    # MEDIO CONOCIDO
    # --------------------------------------------------
    for domain in KNOWN_MEDIA:
        if domain in u:
            return {
                "trust_level": 0.85,
                "type": "recognized_media",
                "reason": "medio reconocido"
            }

    # --------------------------------------------------
    # DOMINIOS SOSPECHOSOS
    # --------------------------------------------------
    for pattern in LOW_QUALITY_PATTERNS:
        if pattern in u:
            return {
                "trust_level": 0.3,
                "type": "low_quality",
                "reason": "dominio de baja calidad o viral"
            }

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------
    return {
        "trust_level": 0.6,
        "type": "generic",
        "reason": "fuente no categorizada"
    }