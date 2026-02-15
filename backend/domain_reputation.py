# backend/domain_reputation.py

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
    parsed = urlparse(url)
    return parsed.netloc.lower()


def calculate_domain_score(url: str) -> dict:
    domain = extract_domain(url)

    score = 0
    signals_positive = []
    signals_negative = []

    # Trusted full domain match
    if any(trusted in domain for trusted in TRUSTED_DOMAINS):
        score += 30
        signals_positive.append("Dominio reconocido")

    # Trusted TLD
    if any(domain.endswith(tld) for tld in TRUSTED_TLDS):
        score += 25
        signals_positive.append("Dominio institucional")

    # Suspicious TLD
    if any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score -= 20
        signals_negative.append("TLD asociado a spam")

    # Default domain presence
    if score == 0:
        score += 5
        signals_positive.append("Dominio válido")

    return {
        "domain": domain,
        "score": max(min(score, 40), 0),  # limitamos a 0-40
        "signals_positive": signals_positive,
        "signals_negative": signals_negative
    }
