"""
Qualitative Risk Engine
=======================
أبسط طريقة لتقييم المخاطر: احتمالية الحدوث (Likelihood) × شدة التأثير (Impact)
كل واحدة فيهم من 1 لـ 5، والنتيجة بتتحول لمستوى خطر (Low/Medium/High/Critical)
دي أول حاجة بتتعلمها في أي معيار زي ISO 27005 أو NIST 800-30.
"""

from typing import Literal

RiskLevel = Literal["Low", "Medium", "High", "Critical"]

# مصفوفة 5x5 قياسية (Likelihood x Impact) - ممكن تتعدل حسب سياسة المنظمة
RISK_MATRIX_LABELS = {
    (1, 1): "Low", (1, 2): "Low", (1, 3): "Low", (1, 4): "Medium", (1, 5): "Medium",
    (2, 1): "Low", (2, 2): "Low", (2, 3): "Medium", (2, 4): "Medium", (2, 5): "High",
    (3, 1): "Low", (3, 2): "Medium", (3, 3): "Medium", (3, 4): "High", (3, 5): "High",
    (4, 1): "Medium", (4, 2): "Medium", (4, 3): "High", (4, 4): "High", (4, 5): "Critical",
    (5, 1): "Medium", (5, 2): "High", (5, 3): "High", (5, 4): "Critical", (5, 5): "Critical",
}


def calculate_qualitative_risk(likelihood: int, impact: int) -> dict:
    """
    likelihood, impact: أرقام من 1 (نادر جدًا / تأثير بسيط) لـ 5 (شبه مؤكد / كارثي)
    بترجع score رقمي (للترتيب والمقارنة) + مستوى نصي (للعرض على المستخدم)
    """
    if not (1 <= likelihood <= 5) or not (1 <= impact <= 5):
        raise ValueError("likelihood and impact must be between 1 and 5")

    score = likelihood * impact  # من 1 لـ 25
    level = RISK_MATRIX_LABELS[(likelihood, impact)]

    return {
        "likelihood": likelihood,
        "impact": impact,
        "risk_score": score,
        "risk_level": level,
        "max_score": 25,
    }


def batch_rank(risk_items: list[dict]) -> list[dict]:
    """بتاخد قائمة risk items (فيها risk_score) وترتبهم من الأخطر للأقل."""
    return sorted(risk_items, key=lambda r: r.get("risk_score", 0), reverse=True)
