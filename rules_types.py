# rules_types.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class RuleResult:
    points: float = 0.0
    reasons: List[str] = field(default_factory=list)
    critical: bool = False
    evidence: List[str] = field(default_factory=list)
