"""
Bow-Tie Analysis Engine
========================
A barrier-based risk method that maps a single "Top Event" (the hazard) between
its causes on the left and its consequences on the right - shaped like a bow-tie.

    [Threat 1] --[Preventive Control]--\\                  /--[Mitigating Control]--[Consequence 1]
    [Threat 2] --[Preventive Control]---> [ TOP EVENT ] ---
    [Threat 3] --[Preventive Control]--/                  \\--[Mitigating Control]--[Consequence 2]

Regulators (aviation, oil & gas, increasingly cyber and healthcare) now expect
organizations to show barriers explicitly, not just a single risk score. This
engine follows the "weakest barrier" principle (same idea as the Swiss Cheese
Model): a chain of controls is only as strong as its weakest link, so we don't
just average control effectiveness - we flag the weakest one specifically.
"""


def _validate_effectiveness(value: int, label: str):
    if not (1 <= value <= 5):
        raise ValueError(f"{label} effectiveness must be between 1 (barely works) and 5 (highly reliable)")


def analyze_bowtie(top_event: str, threats: list[dict], consequences: list[dict]) -> dict:
    """
    threats: [{"description": str, "preventive_controls": [{"name": str, "effectiveness": 1-5}, ...]}, ...]
    consequences: [{"description": str, "severity": 1-5, "mitigating_controls": [{"name": str, "effectiveness": 1-5}, ...]}, ...]
    """
    if not threats:
        raise ValueError("At least one threat (cause) is required")
    if not consequences:
        raise ValueError("At least one consequence is required")

    # ---- Left side: preventive barriers ----
    weakest_preventive = None
    all_preventive_scores = []
    threats_analysis = []
    for t in threats:
        controls = t.get("preventive_controls", [])
        if not controls:
            weak = {"name": "(no preventive control defined)", "effectiveness": 0}
        else:
            for c in controls:
                _validate_effectiveness(c["effectiveness"], f"Preventive control '{c['name']}'")
            weak = min(controls, key=lambda c: c["effectiveness"])
            all_preventive_scores.extend(c["effectiveness"] for c in controls)

        if weakest_preventive is None or weak["effectiveness"] < weakest_preventive["effectiveness"]:
            weakest_preventive = {**weak, "threat": t["description"]}

        threats_analysis.append({
            "description": t["description"],
            "weakest_control": weak,
            "control_count": len(controls),
        })

    avg_preventive = sum(all_preventive_scores) / len(all_preventive_scores) if all_preventive_scores else 0

    # ---- Right side: mitigating barriers ----
    weakest_mitigating = None
    consequences_analysis = []
    for c in consequences:
        controls = c.get("mitigating_controls", [])
        if not controls:
            weak = {"name": "(no mitigating control defined)", "effectiveness": 0}
        else:
            for ctrl in controls:
                _validate_effectiveness(ctrl["effectiveness"], f"Mitigating control '{ctrl['name']}'")
            weak = min(controls, key=lambda ctrl: ctrl["effectiveness"])

        if weakest_mitigating is None or weak["effectiveness"] < weakest_mitigating["effectiveness"]:
            weakest_mitigating = {**weak, "consequence": c["description"]}

        # Residual severity: strong mitigating controls reduce the effective severity felt
        reduction_factor = weak["effectiveness"] / 5  # 0 (no protection) to 1 (fully mitigated)
        residual_severity = round(c["severity"] * (1 - reduction_factor * 0.7), 2)  # controls can reduce impact, rarely eliminate it entirely

        consequences_analysis.append({
            "description": c["description"],
            "raw_severity": c["severity"],
            "weakest_control": weak,
            "residual_severity": residual_severity,
        })

    overall_residual_severity = max(c["residual_severity"] for c in consequences_analysis)

    # Overall barrier health: worst-case framing (weakest link principle)
    if avg_preventive == 0:
        barrier_health = "Critical - no effective preventive barriers in place"
    elif weakest_preventive and weakest_preventive["effectiveness"] <= 2:
        barrier_health = "Weak - at least one preventive barrier is unreliable"
    elif avg_preventive >= 4:
        barrier_health = "Strong - preventive barriers are generally reliable"
    else:
        barrier_health = "Moderate - preventive barriers exist but have gaps"

    return {
        "top_event": top_event,
        "threats_analysis": threats_analysis,
        "consequences_analysis": consequences_analysis,
        "weakest_preventive_control": weakest_preventive,
        "weakest_mitigating_control": weakest_mitigating,
        "average_preventive_effectiveness": round(avg_preventive, 2),
        "overall_residual_severity": overall_residual_severity,
        "barrier_health": barrier_health,
    }
