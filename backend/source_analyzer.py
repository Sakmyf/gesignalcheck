def analyze_source(url: str):

    u = url.lower()

    if any(x in u for x in [".gob", ".gov", ".edu"]):
        return {"trust_level": 0.9}

    if any(x in u for x in ["facebook", "instagram", "tiktok"]):
        return {"trust_level": 0.4}

    if any(x in u for x in ["mercadolibre", "amazon"]):
        return {"trust_level": 0.8}

    return {"trust_level": 0.55}