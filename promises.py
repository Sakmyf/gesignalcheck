import re
from .engine import RuleResult

PROMISE_PATTERNS = [
    r"ganá dinero",
    r"dinero rápido",
    r"sin experiencia",
    r"resultados garantizados",
    r"100% seguro",
    r"en pocos días",
]

def check_promises(text: str) -> RuleResult:
    for p in PROMISE_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return RuleResult(0.25, ["exaggerated_promises"])
    return RuleResult()
