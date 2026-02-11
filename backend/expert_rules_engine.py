import re
from urllib.parse import urlparse

# ======================================================
# ⚖️ Pesos de señales (NO SE USAN POR AHORA, SE CONSERVAN)
# ======================================================
WEIGHTS = {
    "categorical_claim": 1.0,
    "emotional_tone": 0.8,
    "absolute_generalization": 1.0,
    "serious_accusation": 2.8,
    "conspiracy_language": 3.0,
    "no_sources_with_accusations": 2.0,
}

# ======================================================
# 🔍 Helpers
# ======================================================
def contains(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def count(patterns, text):
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)

# ======================================================
# 🌐 Tipo de sitio
# ======================================================
def detect_site_type(url: str) -> str:
    if not url:
        return "unknown"

    domain = urlparse(url).netloc.lower()

    if any(k in domain for k in [".gob.", ".gov.", ".edu.", "indec", "estadistica"]):
        return "institutional"

    if any(k in domain for k in [
        "clarin", "lanacion", "iprofesional", "infobae", "perfil",
        "ambito", "cronista", "bbc", "guardian", "reuters",
        "bloomberg", "nyt", "elpais", "lemonde", "dw", "cnn"
    ]):
        return "media"

    if any(k in domain for k in [
        "facebook", "twitter", "x.com", "instagram", "tiktok", "youtube"
    ]):
        return "social"

    return "blog"

# ======================================================
# 🧠 Engine principal (VERSIÓN CORRECTA)
# ======================================================
def analyze_text(text: str, page_type: str = "unknown", url: str = ""):
    risk_disinformation = 0.0
    risk_opinion = 0.0
    signals = []

    site_type = page_type if page_type != "unknown" else detect_site_type(url)

    # ===============================
    # OPINIÓN / RETÓRICA
    # ===============================
    if contains([
        r"creo que",
        r"en mi opinión",
        r"parece que",
        r"podría ser",
        r"considero que"
    ], text):
        risk_opinion += 1.5
        signals.append("Lenguaje de opinión")

    if count([
        r"escándalo", r"grave", r"indignante",
        r"urgente", r"alarmante", r"terrible"
    ], text) >= 2:
        risk_opinion += 1.0
        signals.append("Lenguaje emocional")

    # ===============================
    # DESINFORMACIÓN
    # ===============================
    if contains([
        r"fraude", r"estafa", r"corrupción",
        r"manipulación", r"engaño"
    ], text):
        risk_disinformation += 2.5
        signals.append("Acusaciones graves")

        if not contains([r"http", r"según", r"fuente", r"informe"], text):
            risk_disinformation += 2.0
            signals.append("Acusaciones sin fuentes")

    if contains([
        r"no quieren que sepas",
        r"te están ocultando",
        r"nadie habla de esto",
        r"verdad oculta"
    ], text):
        risk_disinformation += 3.0
        signals.append("Lenguaje conspirativo")

    # ===============================
    # MODULADORES POR TIPO DE SITIO
    # ===============================
    if site_type == "institutional":
        risk_disinformation *= 0.3
        risk_opinion *= 0.5

    elif site_type == "media":
        risk_disinformation *= 0.6
        risk_opinion *= 0.8

    elif site_type == "social":
        risk_disinformation *= 1.3

    # ===============================
    # DECISIÓN FINAL (TABLA)
    # ===============================
    if risk_disinformation >= 4.5:
        status = "red"
    elif risk_opinion >= 2.0:
        status = "yellow"
    else:
        status = "green"

    return {
        "status": status,
        "score": round(risk_disinformation + risk_opinion, 2),
        "signals": signals,
        "site_type": site_type,
        "risk_disinformation": round(risk_disinformation, 2),
        "risk_opinion": round(risk_opinion, 2)
    }
