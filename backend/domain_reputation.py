# ======================================================
# DOMAIN REPUTATION — SOURCE LAYER
# ======================================================

from urllib.parse import urlparse


TRUSTED_TLDS = [".gov", ".gob", ".edu"]

TRUSTED_DOMAINS = [
    "theguardian.com",
    "iprofesional.com",
    "buenosaires.gob.ar",
    "afip.gob.ar"
]

SUSPICIOUS_TLDS = [".xyz", ".top", ".click", ".info"]


def extract_domain(url: str) -> str:
    if not url:
        return ""

    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""


def calculate_domain_score(url: str) -> dict:

    domain = extract_domain(url)

    if not domain:
        return {
            "domain": "",
            "score": 0,
            "signals_positive": [],
            "signals_negative": []
        }

    score = 0
    signals_positive = []
    signals_negative = []

    # Trusted domain
    if any(trusted in domain for trusted in TRUSTED_DOMAINS):
        score += 30
        signals_positive.append("dominio reconocido")

    # Trusted TLD
    if any(domain.endswith(tld) for tld in TRUSTED_TLDS):
        score += 25
        signals_positive.append("dominio institucional")

    # Suspicious TLD
    if any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score -= 20
        signals_negative.append("tld sospechoso")

    # Default
    if score == 0:
        score += 5
        signals_positive.append("dominio válido")

    return {
        "domain": domain,
        "score": max(min(score, 40), 0),
        "signals_positive": signals_positive,
        "signals_negative": signals_negative
    }