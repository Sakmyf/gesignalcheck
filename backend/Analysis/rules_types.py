# rules_types.py

class RuleResult:
    """
    Resultado estándar que devuelve cada módulo del motor.
    Representa acumulación de puntos de riesgo, razones internas
    y evidencia explicativa para el usuario.
    """

    def __init__(self, points=0.0, reasons=None, evidence=None):
        self.points = float(points)
        self.reasons = reasons[:] if reasons else []
        self.evidence = evidence[:] if evidence else []

    def merge(self, other):
        """
        Combina otro RuleResult dentro de este.
        """
        if not isinstance(other, RuleResult):
            return

        self.points += other.points

        for r in other.reasons:
            if r not in self.reasons:
                self.reasons.append(r)

        for e in other.evidence:
            if e not in self.evidence:
                self.evidence.append(e)

    def clamp(self, min_value=0.0, max_value=10.0):
        """
        Limita los puntos dentro de un rango.
        """
        if self.points < min_value:
            self.points = min_value
        if self.points > max_value:
            self.points = max_value

    def is_empty(self):
        return self.points == 0 and not self.reasons and not self.evidence

    def __repr__(self):
        return f"<RuleResult points={self.points} reasons={len(self.reasons)} evidence={len(self.evidence)}>"