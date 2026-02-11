import re
from urllib.parse import urlparse

# ======================================================
# ⚖️ Pesos de señales (afinados)
# ======================================================
WEIGHTS = {
    "categorical_claim": 1.2,
    "emotional_tone": 0.8,
    "absolute_generalization": 1.0,
    "serious_accusation": 2.5,
    "conspiracy_language": 2.5,
    "no_sources_with_accusations": 1.5,
}

# ======================================================
# 🔍 Helpers
# ======================================================
def contains(patterns, text):
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def count(patterns, text):
    total = 0
    for p in patterns:
        total += len(re.findall(p, text, re.IGNORECASE))
    return total


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
        "clarin", "lanacion", "guardian", "nyt", "bbc",
        "reuters", "elpais", "cnn"
    ]):
        return "media"

    if any(k in domain for k in [
        "facebook", "twitter", "x.com", "instagram", "tiktok", "youtube"
    ]):
        return "social"

    return "blog"


# ======================================================
# 🧠 Engine principal
# ======================================================
def analyze_context(text: str, url: str = ""):
    score = 0.0
    signals = []

    site_type = detect_site_type(url)

    # --------------------------------------------------
    # 1️⃣ Afirmaciones categóricas (NO cualquier "es")
    # --------------------------------------------------
    if contains([
        r"es un hecho",
        r"está probado",
        r"sin dudas",
        r"la verdad es",
        r"queda demostrado",
    ], text):
        score += WEIGHTS["categorical_claim"]
        signals.append("Afirmaciones categóricas")

    # --------------------------------------------------
    # 2️⃣ Tono emocional (solo si es reiterado)
    # --------------------------------------------------
    if count([
        r"escándalo", r"grave", r"indignante",
        r"urgente", r"terrible", r"alarmante"
    ], text) >= 2:
        score += WEIGHTS["emotional_tone"]
        signals.append("Lenguaje emocional reiterado")

    # --------------------------------------------------
    # 3️⃣ Generalizaciones absolutas (solo si se repiten)
    # --------------------------------------------------
    if count([r"todos", r"nadie", r"siempre", r"nunca"], text) >= 2:
        score += WEIGHTS["absolute_generalization"]
        signals.append("Generalizaciones absolutas reiteradas")

    # --------------------------------------------------
    # 4️⃣ Acusaciones graves
    # --------------------------------------------------
    if contains([
        r"fraude", r"estafa", r"corrupción",
        r"manipulación", r"engaño"
    ], text):
        score += WEIGHTS["serious_accusation"]
        signals.append("Acusaciones graves")

        # Falta de fuentes SOLO si hay acusaciones
        if not contains([r"http", r"fuente", r"según", r"informe"], text):
            score += WEIGHTS["no_sources_with_accusations"]
            signals.append("Acusaciones sin fuentes visibles")

    # --------------------------------------------------
    # 5️⃣ Lenguaje conspirativo
    # --------------------------------------------------
    if contains([
        r"nadie habla de",
        r"no quieren que sepas",
        r"te ocultan",
        r"verdad oculta"
    ], text):
        score += WEIGHTS["conspiracy_language"]
        signals.append("Lenguaje conspirativo")

    # --------------------------------------------------
    # 6️⃣ Ajuste por tipo de sitio
    # --------------------------------------------------
    if site_type == "institutional":
        score *= 0.3
    elif site_type == "media":
        score *= 0.6
    elif site_type == "social":
        score *= 1.2

    # --------------------------------------------------
    # 7️⃣ Decisión final (UMBRAL CORREGIDO)
    # --------------------------------------------------
    if score < 3.5:
        status = "green"
        label = "contenido informativo"
    elif score < 6.0:
        status = "yellow"
        label = "requiere lectura crítica"
    else:
        status = "red"
        label = "información cuestionable"

    return {
        "status": status,
        "label": label,
        "score": round(score, 2),
        "signals": signals,
        "site_type": site_type,
    }


# ======================================================
# 🔁 Adaptadores (para tu API actual)
# ======================================================
def engine_context_adapter(text: str, url: str = ""):
    result = analyze_context(text, url)
    return result["score"], result["signals"]


def interpret_score(score: float):
    if score < 3.5:
        return "green", "alto"
    elif score < 6.0:
        return "yellow", "medio"
    else:
        return "red", "bajo"
