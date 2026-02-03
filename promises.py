from rules_types import RuleResult

def check_promises(text: str) -> RuleResult:
    return RuleResult(
        points=0.25,
        reasons=["exaggerated_promises"],
        critical=False
    )
