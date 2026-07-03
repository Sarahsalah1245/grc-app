"""
FMEA Engine (Failure Mode and Effects Analysis)
=================================================
Widely used across manufacturing, IT operations, and safety-critical systems.
Instead of one likelihood x one impact score, FMEA breaks a risk into three
independent factors so you can see WHY something is risky, not just THAT it is:

- Severity (1-10):    how bad are the consequences if the failure happens?
- Occurrence (1-10):  how likely is the failure to happen at all?
- Detection (1-10):   how likely are you to catch it BEFORE it causes harm?
                       (10 = you would almost certainly NOT detect it in time)

RPN (Risk Priority Number) = Severity x Occurrence x Detection   (range 1-1000)

FMEA's real strength is prioritization across many failure modes at once -
it tells you which of dozens of possible failures to fix first.
"""

RPN_THRESHOLDS = [
    (1, 80, "Low"),
    (81, 200, "Medium"),
    (201, 500, "High"),
    (501, 1000, "Critical"),
]


def _rpn_level(rpn: int) -> str:
    for low, high, label in RPN_THRESHOLDS:
        if low <= rpn <= high:
            return label
    return "Critical"


def calculate_fmea(severity: int, occurrence: int, detection: int) -> dict:
    for name, val in [("severity", severity), ("occurrence", occurrence), ("detection", detection)]:
        if not (1 <= val <= 10):
            raise ValueError(f"{name} must be between 1 and 10")

    rpn = severity * occurrence * detection
    return {
        "severity": severity,
        "occurrence": occurrence,
        "detection": detection,
        "rpn": rpn,
        "max_rpn": 1000,
        "risk_level": _rpn_level(rpn),
    }


def rank_failure_modes(modes: list[dict]) -> list[dict]:
    """
    modes: [{"name": "...", "rpn": 240, ...}, ...]
    Sorts failure modes from highest to lowest RPN - this IS the point of FMEA:
    it tells you which failure to fix first when you have many candidates.
    """
    return sorted(modes, key=lambda m: m.get("rpn", 0), reverse=True)
