# ======================================================
# SIGNALCHECK — BASE RESULT (ENGINE v8.7)
# ======================================================

from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisResult:
    points: float = 0.0
    reasons: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)