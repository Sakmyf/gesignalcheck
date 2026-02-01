# rules/types.py
from dataclasses import dataclass
from typing import List

@dataclass
class RuleResult:
    score: float
    evidence: List[str]
