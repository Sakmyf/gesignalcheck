# ======================================================
# SIGNALCHECK ENGINE v11 – CONTEXT AWARE PRO
# ======================================================

from backend.Analysis.credibility import analyze as analyze_credibility
from backend.Analysis.contradictions import analyze_contradictions
from backend.Analysis.authority import analyze_authority
from backend.Analysis.urgency import check_urgency

from backend.source_analyzer import analyze_source


def analyze_context(text: str, url: str = ""):

    if not text:
        return {
            "score": 0.0,
            "level": "green",
            "message": "Sin contenido",
            "signals": []
        }

    text_lower = text.lower()

    # ======================================================
    # ANALISIS BASE (STRUCTURAL CORE)
    # ======================================================

    credibility = analyze_credibility(text)
    contradictions = analyze_contradictions(text)
    authority = analyze_authority(text)
    urgency = check_urgency(text)

    def get_score(x):
        if isinstance(x, dict):
            return x.get("score", 0.0)
        return getattr(x, "points", 0.0)

    def get_signals(x):
        if isinstance(x, dict):
            return x.get("signals", [])
        return getattr(x, "reasons", [])

    narrative_score = get_score(credibility)
    rhetorical_score = get_score(contradictions)
    authority_score = get_score(authority)
    urgency_score = get_score(urgency)

    # ======================================================
    # SCORE BASE
    # ======================================================

    risk_score = (
        narrative_score * 0.25 +
        rhetorical_score * 0.25 +
        authority_score * 0.15 +
        urgency_score * 0.1
    )

    # ======================================================
    # ANALISIS DE FUENTE
    # ======================================================

    source_info = analyze_source(url)
    trust = source_info.get("trust_level", 0.5)

    if trust >= 0.8:
        risk_score *= 0.5
    elif trust >= 0.6:
        risk_score *= 0.75
    elif trust <= 0.3:
        risk_score *= 1.25

    # ======================================================
    # CONTEXT INTELLIGENCE (CLAVE REAL)
    # ======================================================

    context_signals = []

    # 🔴 EVENTOS IMPROBABLES / SENSACIONALISMO
    weird_patterns = [
        "nadie lo puede creer",
        "insólito",
        "increíble",
        "impensado",
        "escena nunca vista",
        "dejó a todos en shock",
        "algo nunca antes visto",
        "defecar en la mesa",
        "situación absurda"
    ]

    weird_hits = [p for p in weird_patterns if p in text_lower]

    if weird_hits:
        risk_score += 0.3
        context_signals.append("evento_improbable")

    # 🟡 DETECCIÓN DE FACT-CHECK
    factcheck_patterns = [
        "no es cierto",
        "esto es falso",
        "fake",
        "bulo",
        "desmentimos",
        "verificación",
        "fact-check",
        "no ocurrió"
    ]

    factcheck_hits = [p for p in factcheck_patterns if p in text_lower]

    if factcheck_hits:
        risk_score -= 0.25
        context_signals.append("fact_check")

    # 🔵 DETECCIÓN DE NARRATIVA FICTICIA / DRAMATIZADA
    fiction_patterns = [
        "escena imaginada",
        "relato ficticio",
        "historia ficticia",
        "recreación",
        "dramatización"
    ]

    fiction_hits = [p for p in fiction_patterns if p in text_lower]

    if fiction_hits:
        risk_score += 0.2
        context_signals.append("narrativa_ficticia")

    # 🟢 CONTENIDO COMERCIAL (BAJO RIESGO)
    commercial_patterns = [
        "oferta",
        "descuento",
        "precio",
        "comprar",
        "envío",
        "cuotas",
        "promo"
    ]

    commercial_hits = [p for p in commercial_patterns if p in text_lower]

    if commercial_hits:
        risk_score -= 0.2
        context_signals.append("contenido_comercial")

    # ======================================================
    # NORMALIZACIÓN FINAL
    # ======================================================

    risk_score = max(0.0, min(risk_score, 1.0))

    # ======================================================
    # CLASIFICACIÓN FINAL (UX)
    # ======================================================

    if risk_score < 0.3:
        level = "green"
        message = "Bajo riesgo"

    elif risk_score < 0.6:
        level = "yellow"
        message = "Contenido con señales mixtas"

    else:
        level = "red"
        message = "Requiere atención"

    # ======================================================
    # SEÑALES
    # ======================================================

    signals = (
        get_signals(credibility) +
        get_signals(contradictions) +
        get_signals(authority) +
        get_signals(urgency) +
        context_signals +
        source_info.get("signals", [])
    )

    signals = list(set(signals))[:6]

    # ======================================================
    # OUTPUT FINAL
    # ======================================================

    return {
        "score": round(risk_score, 2),
        "level": level,
        "message": message,
        "signals": signals,
        "source": source_info
    }