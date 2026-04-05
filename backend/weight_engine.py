# ======================================================
# SIGNALCHECK – WEIGHT ENGINE v3 (FULL CALIBRATED)
# Combina:
# - ajuste dinámico
# - cálculo real de score
# ======================================================

# ======================================================
# ⚙️ AJUSTE DE PESOS (tu lógica original)
# ======================================================

def adjust_weights(base_weights: dict, context: str, source_info: dict) -> dict:

    weights = base_weights.copy()
    trust = source_info.get("trust_level", 0.55)

    if context == "health_science":
        weights["scientific_claims"] = weights.get("scientific_claims", 0.08) * 1.5
        weights["authority"]         = weights.get("authority", 0.10)         * 1.3
        weights["emotions"]          = weights.get("emotions", 0.12)          * 0.7

    elif context == "politics":
        weights["polarization"]   = weights.get("polarization", 0.12)   * 1.4
        weights["misinformation"] = weights.get("misinformation", 0.10) * 1.2
        weights["emotions"]       = weights.get("emotions", 0.12)       * 1.1

    elif context == "opinion":
        weights["emotions"]     = weights.get("emotions", 0.12)     * 0.6
        weights["polarization"] = weights.get("polarization", 0.12) * 0.7

    elif context == "news":
        weights["credibility"] = weights.get("credibility", 0.15) * 0.7

    if trust > 0.8:
        weights["credibility"]    = weights.get("credibility", 0.15)    * 0.6
        weights["misinformation"] = weights.get("misinformation", 0.10) * 0.7

    elif trust < 0.4:
        weights["credibility"]    = weights.get("credibility", 0.15)    * 1.3
        weights["misinformation"] = weights.get("misinformation", 0.10) * 1.3
        weights["hypothetical"]   = weights.get("hypothetical", 0.05)   * 1.2

    return weights


# ======================================================
# 🧠 CÁLCULO DE RIESGO (LO QUE TE FALTABA)
# ======================================================

def compute_risk(scores: dict, base_weights: dict, context: str, source_info: dict):

    # -------------------------------
    # 1. Ajuste dinámico
    # -------------------------------
    weights = adjust_weights(base_weights, context, source_info)

    # -------------------------------
    # 2. Normalización
    # -------------------------------
    normalized = {}

    for k, v in scores.items():
        try:
            normalized[k] = abs(float(v))
        except:
            normalized[k] = 0.0

    # -------------------------------
    # 3. Raw score
    # -------------------------------
    raw_score = sum(
        normalized.get(k, 0) * weights.get(k, 0.1)
        for k in normalized
    )

    # -------------------------------
    # 4. Escalado (FIX CLAVE)
    # -------------------------------
    risk_score = raw_score ** 0.5

    # -------------------------------
    # 5. Clamp
    # -------------------------------
    risk_score = max(0.08, min(risk_score, 1.0))

    # -------------------------------
    # 6. Score final
    # -------------------------------
    if risk_score < 0.2:
        final_score = int(10 + risk_score * 60)

    elif risk_score < 0.5:
        final_score = int(20 + risk_score * 80)

    else:
        final_score = int(50 + risk_score * 100)

    final_score = min(final_score, 100)

    # -------------------------------
    # 7. Nivel
    # -------------------------------
    if final_score < 30:
        level = "low"
    elif final_score < 60:
        level = "medium"
    else:
        level = "high"

    return {
        "score": final_score,
        "level": level,
        "raw_score": round(raw_score, 4),
        "scaled_score": round(risk_score, 4),
        "weights_used": weights
    }