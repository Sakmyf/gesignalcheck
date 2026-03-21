# ======================================================
# SIGNALCHECK — BASE RESULT (ENGINE v8.7 PRO)
# ======================================================

from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisResult:
    points: float = 0.0
    reasons: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)

    # --------------------------------------------------
    # ➕ AGREGAR RESULTADOS
    # --------------------------------------------------

    def add(self, points: float = 0.0, reason: str = None, evidence: str = None):
        self.points += points

        if reason and reason not in self.reasons:
            self.reasons.append(reason)

        if evidence and evidence not in self.evidence:
            self.evidence.append(evidence)

    # --------------------------------------------------
    # 🔗 MERGE (compatibilidad con otros resultados)
    # --------------------------------------------------

    def merge(self, other):
        if not isinstance(other, AnalysisResult):
            return

        self.points += other.points

        for r in other.reasons:
            if r not in self.reasons:
                self.reasons.append(r)

        for e in other.evidence:
            if e not in self.evidence:
                self.evidence.append(e)

    # --------------------------------------------------
    # 🔒 NORMALIZACIÓN
    # --------------------------------------------------

    def clamp(self, min_value: float = 0.0, max_value: float = 10.0):
        if self.points < min_value:
            self.points = min_value

        if self.points > max_value:
            self.points = max_value

    # --------------------------------------------------
    # 🧪 DEBUG
    # --------------------------------------------------

    def is_empty(self):
        return self.points == 0 and not self.reasons and not self.evidence

    def __repr__(self):
        return (
            f"<AnalysisResult points={self.points} "
            f"reasons={len(self.reasons)} "
            f"evidence={len(self.evidence)}>"
        )