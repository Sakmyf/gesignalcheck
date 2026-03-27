# scam_signals.py

from rules_types import RuleResult
import re


def analyze_scam_signals(text: str, url: str = "") -> RuleResult:

    t = text.lower()
    u = url.lower() if url else ""

    score = 0.0
    reasons = []
    evidence = []

    # 🔴 Dominio sospechoso
    suspicious_domains = [
        ".xyz", ".top", ".shop", ".store", ".online"
    ]

    if any(d in u for d in suspicious_domains):
        score += 0.25
        reasons.append("suspicious_domain")
        evidence.append("Dominio poco confiable detectado")

    # 🔴 Marca premium + precio bajo
    if any(w in t for w in ["iphone", "apple", "samsung"]):
        if re.search(r"\d{2,4}\s?(€|\$|usd)", t):
            price_numbers = re.findall(r"\d{2,4}", t)
            if price_numbers:
                price = int(price_numbers[0])
                if price < 500:
                    score += 0.35
                    reasons.append("unrealistic_price")
                    evidence.append("Precio anormalmente bajo para producto premium")

    # 🔴 Falta de información empresarial
    if not any(w in t for w in ["contacto", "empresa", "about", "legal"]):
        score += 0.10
        reasons.append("missing_business_info")
        evidence.append("Falta información clara de la empresa")

    # 🔴 Reviews fake típicas
    if re.search(r"\b\d{3,5}\s?(reviews|opiniones)", t):
        score += 0.20
        reasons.append("fake_reviews_pattern")
        evidence.append("Patrón típico de reviews falsas")

    # 🔴 Urgencia comercial
    if any(w in t for w in ["only today", "last chance", "limited stock"]):
        score += 0.15
        reasons.append("fake_urgency")
        evidence.append("Urgencia artificial de compra")

    if score == 0:
        return RuleResult()

    return RuleResult(
        points=score,
        reasons=reasons,
        evidence=evidence
    )