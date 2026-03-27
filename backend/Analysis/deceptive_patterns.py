# deceptive.py (MEJORADO)

from rules_types import RuleResult

def analyze_deceptive_patterns(text: str) -> RuleResult:

    t = text.lower()

    score = 0.0
    reasons = []
    evidence = []

    has_discount = False
    has_cta = False
    has_premium = False

    # 🔴 Producto premium
    if any(w in t for w in ["iphone", "samsung", "apple"]):
        has_premium = True

    # 🔴 Descuentos
    if any(w in t for w in ["50% off", "60% off", "70% off", "80% off", "90% off"]):
        score += 0.25
        has_discount = True
        reasons.append("high_discount")
        evidence.append("Descuento alto detectado")

    # 🔴 CTA agresivo
    if any(w in t for w in ["buy now", "shop now", "limited offer", "act now"]):
        score += 0.10
        has_cta = True
        reasons.append("aggressive_cta")
        evidence.append("Llamado a la acción agresivo")

    # 🔴 Reviews sospechosas
    if any(w in t for w in ["1,231", "1231", "5000 reviews", "10,000 reviews"]):
        score += 0.20
        reasons.append("suspicious_reviews")
        evidence.append("Cantidad de reviews sospechosa")

    # 🔥 COMBO BOOST (clave)
    if has_premium and has_discount:
        score += 0.25
        reasons.append("premium_discount_combo")
        evidence.append("Producto premium con descuento fuerte")

    if has_discount and has_cta:
        score += 0.15
        reasons.append("pressure_sale_combo")
        evidence.append("Descuento + presión de compra")

    if has_premium and has_cta:
        score += 0.10

    if score == 0:
        return RuleResult()

    return RuleResult(
        points=score,
        reasons=reasons,
        evidence=evidence
    )