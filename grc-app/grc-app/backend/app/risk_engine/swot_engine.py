"""
SWOT Engine
===========
مش مجرد ليستة نصوص - بنحول كل بند لوزن رقمي (1-5) عشان نقدر نطلع:
- TOWS matrix أساسي (إزاي نستخدم القوة عشان نقابل التهديد... الخ)
- أكتر التهديدات والنقاط الضعف "خطورة" عشان تتربط بمحرك المخاطر (Risk Engine)
"""

from collections import defaultdict

CATEGORIES = ["strength", "weakness", "opportunity", "threat"]


def score_swot(entries: list[dict]) -> dict:
    """
    entries: [{"category": "threat", "description": "...", "weight": 4}, ...]
    """
    grouped = defaultdict(list)
    totals = defaultdict(int)

    for e in entries:
        cat = e["category"]
        if cat not in CATEGORIES:
            raise ValueError(f"category must be one of: {CATEGORIES}")
        grouped[cat].append(e)
        totals[cat] += e.get("weight", 3)

    # صافي الوضع الداخلي (قوة - ضعف) والخارجي (فرص - تهديدات)
    internal_balance = totals["strength"] - totals["weakness"]
    external_balance = totals["opportunity"] - totals["threat"]

    # ترتيب التهديدات ونقاط الضعف الأعلى وزنًا - دي اللي المفروض تتحول لـ Risk Items
    top_threats = sorted(grouped["threat"], key=lambda e: e.get("weight", 3), reverse=True)
    top_weaknesses = sorted(grouped["weakness"], key=lambda e: e.get("weight", 3), reverse=True)

    if internal_balance >= 0 and external_balance >= 0:
        posture = "SO - Aggressive (leverage your strengths to seize opportunities)"
    elif internal_balance < 0 and external_balance >= 0:
        posture = "WO - Developmental (fix weaknesses first so you can capture opportunities)"
    elif internal_balance >= 0 and external_balance < 0:
        posture = "ST - Defensive (use your strengths to reduce the impact of threats)"
    else:
        posture = "WT - Survival (top priority: reduce the biggest weaknesses and threats immediately)"

    return {
        "totals": dict(totals),
        "internal_balance": internal_balance,
        "external_balance": external_balance,
        "strategic_posture": posture,
        "top_threats": top_threats[:5],
        "top_weaknesses": top_weaknesses[:5],
        "suggested_risk_candidates": [
            {"source": "threat", **t} for t in top_threats[:3]
        ] + [
            {"source": "weakness", **w} for w in top_weaknesses[:3]
        ],
    }
