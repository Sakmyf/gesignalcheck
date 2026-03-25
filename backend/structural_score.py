# ======================================================
# SIGNALCHECK – STRUCTURAL SCORE v1.1 (MEJORADO)
# ======================================================

def calculate_structural_score(results: dict):

    emotionality = (
        results.get("emotions", 0) +
        results.get("polarization", 0)
    ) / 2

    manipulation = (
        results.get("urgency", 0) +
        results.get("promises", 0) +
        results.get("narrative_patterns", 0)
    ) / 3

    lack_of_evidence = (
        results.get("scientific_claims", 0) +
        (1 - results.get("credibility", 1))
    ) / 2

    # 🔥 MEJORADO
    incoherence = (
        results.get("contradictions", 0) +
        (1 - results.get("credibility", 1)) * 0.5
    ) / 1.5

    score = (
        emotionality * 0.25 +
        manipulation * 0.25 +
        lack_of_evidence * 0.25 +
        incoherence * 0.25
    )

    return round(score * 100, 2)