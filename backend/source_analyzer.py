# ======================================================
# SOURCE ANALYZER — FIXED VERSION
# ======================================================

def analyze_source(url: str):

    if not url:
        return {
            "domain": "",
            "trust_level": 0.5,
            "type": "unknown",
            "signals": ["sin información de fuente"]
        }

    u = url.lower()

    # --------------------------------------------------
    # 🟢 ALTA CONFIANZA
    # --------------------------------------------------
    high_trust = [
        "argentina.gob.ar",
        "gov.ar",
        "who.int",
        "un.org",
        "vatican.va"
    ]

    # --------------------------------------------------
    # 🟡 MEDIA
    # --------------------------------------------------
    medium_trust = [
        "clarin.com",
        "lanacion.com.ar",
        "infobae.com"
    ]

    # --------------------------------------------------
    # 🔴 BAJA
    # --------------------------------------------------
    low_trust = [
        "cronica.com.ar",
        ".click",
        ".xyz",
        ".top"
    ]

    # --------------------------------------------------
    # MATCH
    # --------------------------------------------------

    for d in high_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.95,
                "type": "high_trust",
                "signals": ["fuente institucional confiable"]
            }

    for d in medium_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.7,
                "type": "medium_trust",
                "signals": ["medio reconocido"]
            }

    for d in low_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.3,
                "type": "low_trust",
                "signals": ["fuente de baja calidad"]
            }

    return {
        "domain": "unknown",
        "trust_level": 0.5,
        "type": "neutral",
        "signals": ["fuente no categorizada"]
    }