"""
Quantitative Risk Engine
========================
بيحول الخطر لأرقام فلوس فعلية (بالعملة اللي انتي هتحدديها)، وده اللي
بتطلبه الإدارة العليا والمجالس عشان يقارنوا تكلفة الخطر بتكلفة الحل.

المفاهيم (معيار NIST / ISO 27005 / معايير الـ FAIR الأساسية):
- Asset Value (AV): قيمة الأصل (سيرفر، قاعدة بيانات، سمعة الشركة... الخ)
- Exposure Factor (EF): نسبة الأصل اللي هتتدمر لو الخطر حصل (0 لـ 1)
- SLE = AV * EF                      -> Single Loss Expectancy (خسارة الحادثة الواحدة)
- ARO = عدد مرات الحدوث المتوقعة في السنة (ممكن تكون كسر: 0.1 يعني مرة كل 10 سنين)
- ALE = SLE * ARO                    -> Annual Loss Expectancy (الخسارة السنوية المتوقعة)
- ROSI = (ALE_before - ALE_after - Cost_of_control) / Cost_of_control  -> عائد الاستثمار في الحل الأمني
"""


def calculate_sle(asset_value: float, exposure_factor: float) -> float:
    if not (0 <= exposure_factor <= 1):
        raise ValueError("exposure_factor must be between 0 and 1")
    if asset_value < 0:
        raise ValueError("asset_value must be a positive number")
    return round(asset_value * exposure_factor, 2)


def calculate_ale(sle: float, aro: float) -> float:
    if aro < 0:
        raise ValueError("aro must be a positive number (or zero)")
    return round(sle * aro, 2)


def calculate_quantitative_risk(asset_value: float, exposure_factor: float, aro: float) -> dict:
    sle = calculate_sle(asset_value, exposure_factor)
    ale = calculate_ale(sle, aro)
    return {
        "asset_value": asset_value,
        "exposure_factor": exposure_factor,
        "sle": sle,
        "aro": aro,
        "ale": ale,
    }


def calculate_rosi(ale_before: float, ale_after: float, cost_of_control: float) -> dict:
    """
    ROSI = Return On Security Investment
    بتستخدم عشان تثبتي إن شراء ضابط أمني (control) معين يستاهل فلوسه أو لأ.
    """
    if cost_of_control <= 0:
        raise ValueError("cost_of_control must be greater than zero")

    risk_reduction = ale_before - ale_after
    rosi = (risk_reduction - cost_of_control) / cost_of_control

    return {
        "ale_before": ale_before,
        "ale_after": ale_after,
        "cost_of_control": cost_of_control,
        "risk_reduction": round(risk_reduction, 2),
        "rosi_percentage": round(rosi * 100, 2),
        "is_worth_it": rosi > 0,
    }
