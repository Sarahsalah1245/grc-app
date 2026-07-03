from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import (QualitativeRequest, QuantitativeRequest, RosiRequest,
                          MonteCarloRequest, FullRiskAnalysisRequest, FmeaRequest, BowtieRequest)
from app.risk_engine.qualitative import calculate_qualitative_risk
from app.risk_engine.quantitative import calculate_quantitative_risk, calculate_rosi
from app.risk_engine.monte_carlo import run_monte_carlo_simulation
from app.risk_engine.fmea import calculate_fmea
from app.risk_engine.bowtie import analyze_bowtie
from app.llm import xai
from app.llm.cobit_rag import map_risk_to_cobit

router = APIRouter(prefix="/risks", tags=["Risk Calculations"])


@router.post("/qualitative")
def qualitative(payload: QualitativeRequest, user: User = Depends(get_current_user)):
    result = calculate_qualitative_risk(payload.likelihood, payload.impact)
    return result


@router.post("/qualitative/explain")
def qualitative_explain(payload: QualitativeRequest, user: User = Depends(get_current_user)):
    result = calculate_qualitative_risk(payload.likelihood, payload.impact)
    result["ai_explanation"] = xai.explain_qualitative(result)
    return result


@router.post("/quantitative")
def quantitative(payload: QuantitativeRequest, user: User = Depends(get_current_user)):
    return calculate_quantitative_risk(payload.asset_value, payload.exposure_factor, payload.aro)


@router.post("/quantitative/explain")
def quantitative_explain(payload: QuantitativeRequest, user: User = Depends(get_current_user)):
    result = calculate_quantitative_risk(payload.asset_value, payload.exposure_factor, payload.aro)
    result["ai_explanation"] = xai.explain_quantitative(result)
    return result


@router.post("/rosi")
def rosi(payload: RosiRequest, user: User = Depends(get_current_user)):
    return calculate_rosi(payload.ale_before, payload.ale_after, payload.cost_of_control)


@router.post("/monte-carlo")
def monte_carlo(payload: MonteCarloRequest, user: User = Depends(get_current_user)):
    return run_monte_carlo_simulation(
        payload.freq_min, payload.freq_most_likely, payload.freq_max,
        payload.mag_min, payload.mag_most_likely, payload.mag_max,
        iterations=payload.iterations,
    )


@router.post("/monte-carlo/explain")
def monte_carlo_explain(payload: MonteCarloRequest, user: User = Depends(get_current_user)):
    result = run_monte_carlo_simulation(
        payload.freq_min, payload.freq_most_likely, payload.freq_max,
        payload.mag_min, payload.mag_most_likely, payload.mag_max,
        iterations=payload.iterations,
    )
    result["ai_explanation"] = xai.explain_monte_carlo(result)
    return result


@router.post("/fmea")
def fmea(payload: FmeaRequest, user: User = Depends(get_current_user)):
    return calculate_fmea(payload.severity, payload.occurrence, payload.detection)


@router.post("/fmea/explain")
def fmea_explain(payload: FmeaRequest, user: User = Depends(get_current_user)):
    result = calculate_fmea(payload.severity, payload.occurrence, payload.detection)
    result["ai_explanation"] = xai.explain_fmea(result)
    return result


@router.post("/bowtie")
def bowtie(payload: BowtieRequest, user: User = Depends(get_current_user)):
    threats = [t.model_dump() for t in payload.threats]
    consequences = [c.model_dump() for c in payload.consequences]
    return analyze_bowtie(payload.top_event, threats, consequences)


@router.post("/bowtie/explain")
def bowtie_explain(payload: BowtieRequest, user: User = Depends(get_current_user)):
    threats = [t.model_dump() for t in payload.threats]
    consequences = [c.model_dump() for c in payload.consequences]
    result = analyze_bowtie(payload.top_event, threats, consequences)
    result["ai_explanation"] = xai.explain_bowtie(result)
    return result


@router.post("/full-analysis")
def full_analysis(payload: FullRiskAnalysisRequest, user: User = Depends(get_current_user)):
    """
    Endpoint واحد بيجمع كل حاجة: qualitative + quantitative + monte carlo (اختياري)
    + شرح AI + ربط بـ COBIT. ده اللي هتستخدمه شاشة "تحليل خطر جديد" في الفرونت اند.
    """
    q = payload.qualitative
    qt = payload.quantitative

    qualitative_result = calculate_qualitative_risk(q.likelihood, q.impact)
    quantitative_result = calculate_quantitative_risk(qt.asset_value, qt.exposure_factor, qt.aro)

    monte_carlo_result = None
    if payload.monte_carlo:
        mc = payload.monte_carlo
        monte_carlo_result = run_monte_carlo_simulation(
            mc.freq_min, mc.freq_most_likely, mc.freq_max,
            mc.mag_min, mc.mag_most_likely, mc.mag_max,
            iterations=mc.iterations,
        )

    cobit_mapping = None
    if payload.map_to_cobit:
        cobit_mapping = map_risk_to_cobit(f"{payload.asset_name}: {payload.threat_description}")

    ai_explanation = None
    if payload.generate_ai_explanation:
        # بنجمع خلاصة الثلاث حسابات في شرح واحد متكامل
        combined = {**qualitative_result, **quantitative_result}
        ai_explanation = {
            "qualitative": xai.explain_qualitative(qualitative_result),
            "quantitative": xai.explain_quantitative(quantitative_result),
        }
        if monte_carlo_result:
            ai_explanation["monte_carlo"] = xai.explain_monte_carlo(monte_carlo_result)

    return {
        "asset_name": payload.asset_name,
        "threat_description": payload.threat_description,
        "qualitative": qualitative_result,
        "quantitative": quantitative_result,
        "monte_carlo": monte_carlo_result,
        "cobit_mapping": cobit_mapping,
        "ai_explanation": ai_explanation,
    }
