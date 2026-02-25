print("ENGINE VERSION 2.0 ACTIVO")
import re
from urllib.parse import urlparse

# ======================================================
# ⚖️ Pesos de señales (calibrados profesionalmente)
# ======================================================
WEIGHTS = {
    "categorical_claim": 0.6,
    "emotional_tone": 0.4,
    "absolute_generalization": 0.7,
    "serious_accusation": 1.5,
    "conspiracy_language": 1.5,
    "no_sources_with_accusations": 1.0,
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
    # 1️⃣ Afirmaciones categóricas
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
    # 2️⃣ Tono emocional reiterado
    # --------------------------------------------------
    if count([
        r"escándalo", r"grave", r"indignante",
        r"urgente", r"terrible", r"alarmante"
    ], text) >= 2:
        score += WEIGHTS["emotional_tone"]
        signals.append("Lenguaje emocional reiterado")

    # --------------------------------------------------
    # 3️⃣ Generalizaciones absolutas reiteradas
    # --------------------------------------------------
    if count([r"todos", r"nadie", r"siempre", r"nunca"], text) >= 2:
        score += WEIGHTS["absolute_generalization"]
        signals.append("Generalizaciones absolutas reiteradas")

    # --------------------------------------------------
    # 4️⃣ Acusaciones graves sin atribución
    # --------------------------------------------------
    if contains([
        r"fraude", r"estafa", r"corrupción",
        r"manipulación", r"engaño"
    ], text):

        if not contains([
            r"según",
            r"dijo",
            r"informó",
            r"declaró",
            r"reportó",
            r"informe",
            r"de acuerdo con"
        ], text):

            score += WEIGHTS["serious_accusation"]
            signals.append("Acusaciones sin atribución clara")

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

    # ======================================================
    # 🔧 Ajuste por tipo de sitio
    # ======================================================
    if site_type == "institutional":
        score *= 0.6
    elif site_type == "media":
        score *= 0.85
    elif site_type == "social":
        score *= 1.15

    # ======================================================
    # 📊 Normalización profesional
    # ======================================================
    max_possible_score = sum(WEIGHTS.values())
    normalized_score = score / max_possible_score
    normalized_score = max(min(normalized_score, 1.0), 0.0)

    # Si no hay señales, score mínimo
    if len(signals) == 0:
        normalized_score = 0.05

    score = normalized_score

    # ======================================================
    # 🚦 Decisión final coherente (escala 0–1)
    # ======================================================
    if score < 0.25:
        status = "green"
        label = "contenido informativo"
    elif score < 0.55:
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
# 🔁 Adaptadores
# ======================================================
def engine_context_adapter(text: str, url: str = ""):
    result = analyze_context(text, url)
    return result["score"], result["signals"]


def interpret_score(score: float):
    if score < 0.25:
        return "green", "bajo"
    elif score < 0.55:
        return "yellow", "medio"
    else:
        return "red", "alto"