# ======================================================
# SOURCE ANALYZER — EXPANDED COVERAGE
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
    # 🟢 ALTA CONFIANZA (0.90–0.95)
    # Institucionales, académicos, organismos internacionales
    # --------------------------------------------------
    high_trust = [
        # Argentina gobierno
        "argentina.gob.ar", "gov.ar", "gob.ar",
        # Organismos internacionales
        "who.int", "un.org", "unesco.org", "paho.org",
        "worldbank.org", "imf.org", "oas.org",
        # Religioso institucional
        "vatican.va",
        # Académicos genéricos
        ".edu.ar", ".edu",
        # Fact-checkers reconocidos
        "chequeado.com", "snopes.com", "factcheck.org",
        "fullfact.org", "politifact.com",
    ]

    # --------------------------------------------------
    # 🟡 CONFIANZA MEDIA-ALTA (0.72)
    # Medios establecidos LATAM + internacionales
    # --------------------------------------------------
    medium_high_trust = [
        # Argentina
        "clarin.com", "lanacion.com.ar", "infobae.com",
        "pagina12.com.ar", "cronista.com", "ambito.com",
        "telam.com.ar", "perfil.com",
        # Internacional
        "bbc.com", "reuters.com", "apnews.com",
        "theguardian.com", "elpais.com", "elmundo.es",
        "nytimes.com", "washingtonpost.com",
        "dw.com", "france24.com",
        # LATAM
        "eluniversal.com", "eltiempo.com", "folha.uol.com.br",
    ]

    # --------------------------------------------------
    # 🟡 CONFIANZA MEDIA (0.60)
    # Medios regionales, blogs con trayectoria, ecommerce conocido
    # --------------------------------------------------
    medium_trust = [
        # Ecommerce establecido
        "mercadolibre.com", "amazon.com", "garbarino.com.ar",
        "fravega.com", "musimundo.com",
        # Redes/plataformas
        "youtube.com", "twitter.com", "x.com",
        "linkedin.com", "facebook.com",
        # Medios menores conocidos
        "cronica.com.ar", "minutouno.com", "eldestape.com.ar",
    ]

    # --------------------------------------------------
    # 🔴 BAJA CONFIANZA (0.25)
    # TLDs sospechosos, dominios de spam conocidos
    # --------------------------------------------------
    low_trust = [
        ".click", ".xyz", ".top", ".tk", ".ml", ".ga", ".cf",
        "bit.ly", "tinyurl.com", "t.co/",
    ]

    # --------------------------------------------------
    # MATCH — orden importa (más específico primero)
    # --------------------------------------------------

    for d in high_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.92,
                "type": "high_trust",
                "signals": ["fuente institucional o verificadora confiable"]
            }

    for d in medium_high_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.72,
                "type": "medium_high_trust",
                "signals": ["medio de comunicación establecido"]
            }

    for d in medium_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.60,
                "type": "medium_trust",
                "signals": ["fuente conocida, contexto variable"]
            }

    for d in low_trust:
        if d in u:
            return {
                "domain": d,
                "trust_level": 0.25,
                "type": "low_trust",
                "signals": ["dominio o acortador de baja confianza"]
            }

    # --------------------------------------------------
    # DEFAULT: desconocido → trust neutral-positivo
    # Antes: 0.5 sin ajuste → acumulaba riesgo
    # Ahora: 0.55 → leve beneficio de la duda
    # La mayoría de URLs desconocidas son sitios legítimos
    # --------------------------------------------------
    return {
        "domain": "unknown",
        "trust_level": 0.55,
        "type": "neutral",
        "signals": []   # sin señal → no contamina el output
    }