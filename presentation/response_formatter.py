# ======================================================
# SIGNALCHECK – RESPONSE FORMATTER v1.0
# Convierte el análisis en algo usable
# ======================================================

def format_response(result: dict):
    """
    Convierte output técnico → output para usuario
    """

    level = result.get("risk_level", "low")
    insight = result.get("insight", "")
    reasons = result.get("reasons", [])
    profile = result.get("profile", {})

    # --------------------------------------------------
    # SEMÁFORO
    # --------------------------------------------------
    if level == "low":
        emoji = "🟢"
        label = "Riesgo Bajo"
    elif level == "medium":
        emoji = "🟡"
        label = "Riesgo Medio"
    else:
        emoji = "🔴"
        label = "Riesgo Alto"

    # --------------------------------------------------
    # TOP 3 REASONS
    # --------------------------------------------------
    top_reasons = reasons[:3]

    # --------------------------------------------------
    # PERFIL SIMPLIFICADO
    # --------------------------------------------------
    profile_view = {
        "emocionalidad": round(profile.get("emocionalidad", 0), 2),
        "manipulacion": round(profile.get("manipulacion", 0), 2),
        "confiabilidad": round(profile.get("confiabilidad", 0), 2),
    }

    # --------------------------------------------------
    # OUTPUT FINAL
    # --------------------------------------------------
    return {
        "status": f"{emoji} {label}",
        "insight": insight,
        "claves": top_reasons,
        "perfil": profile_view
    }