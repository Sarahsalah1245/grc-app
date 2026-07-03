"""
XAI (Explainable AI) Module
============================
Every numeric result (Monte Carlo, ALE, FMEA, Bow-Tie...) is paired with a
plain-language explanation of "why the result came out this way" - research
consistently points to this as the biggest missing piece in AI-assisted GRC
tools today.

Important: the LLM does NOT calculate any numbers here. All numbers come from
risk_engine (deterministic, fully auditable Python code). The LLM's only job
is to explain numbers that were already computed - this is exactly how we
avoid the hallucination problem: we never let the model "invent" figures, we
only let it explain figures we computed ourselves.
"""

from app.llm.groq_client import chat_completion

SYSTEM_PROMPT = """You are an expert assistant in IT governance and risk management (GRC) and the COBIT 2019 framework.
Your only job is to explain ready-made calculation results in simple, clear language, without inventing any new numbers.
- Use only the exact numbers given to you.
- Explain why we arrived at this result, and what it means practically for a decision-maker.
- Suggest one or two practical actions based on the risk level.
- Be concise (no more than 6 lines) and direct."""


def explain_qualitative(result: dict) -> str:
    prompt = f"""Qualitative risk assessment result:
- Likelihood: {result['likelihood']}/5
- Impact severity: {result['impact']}/5
- Risk score: {result['risk_score']}/25
- Final classification: {result['risk_level']}

Explain to the user what this classification means and what action it calls for."""
    return chat_completion(SYSTEM_PROMPT, prompt)


def explain_quantitative(result: dict) -> str:
    prompt = f"""Quantitative risk assessment result (ALE):
- Asset value: {result['asset_value']}
- Exposure Factor: {result['exposure_factor']}
- Single Loss Expectancy (SLE): {result['sle']}
- Annual Rate of Occurrence (ARO): {result['aro']}
- Annual Loss Expectancy (ALE): {result['ale']}

Explain to the user what this ALE value means in practice, and whether it justifies investing in additional security controls."""
    return chat_completion(SYSTEM_PROMPT, prompt)


def explain_monte_carlo(result: dict) -> str:
    prompt = f"""Monte Carlo simulation result for a given risk (number of scenarios: {result['iterations']}):
- Mean annual loss: {result['mean_annual_loss']}
- Median: {result['median_annual_loss']}
- Value at Risk at 95% confidence (VaR 95%): {result['value_at_risk_95']}
- Value at Risk at 99% confidence (VaR 99%): {result['value_at_risk_99']}
- Maximum simulated loss: {result['max_loss']}

Explain what VaR 95% means in plain language (e.g. "we are 95% confident our annual loss will not exceed X"),
and why this approach is more accurate than a single fixed-number calculation."""
    return chat_completion(SYSTEM_PROMPT, prompt)


def explain_fmea(result: dict) -> str:
    prompt = f"""FMEA (Failure Mode and Effects Analysis) result:
- Severity: {result['severity']}/10
- Occurrence: {result['occurrence']}/10
- Detection: {result['detection']}/10
- Risk Priority Number (RPN): {result['rpn']}/1000
- Risk level: {result['risk_level']}

Explain what this RPN means, which of the three factors (severity, occurrence, detection) is driving the risk the most,
and suggest one concrete way to reduce the RPN."""
    return chat_completion(SYSTEM_PROMPT, prompt)


def explain_bowtie(result: dict) -> str:
    prompt = f"""Bow-Tie analysis result for top event "{result['top_event']}":
- Barrier health: {result['barrier_health']}
- Average preventive control effectiveness: {result['average_preventive_effectiveness']}/5
- Weakest preventive control: {result['weakest_preventive_control']}
- Weakest mitigating control: {result['weakest_mitigating_control']}
- Overall residual severity after mitigation: {result['overall_residual_severity']}

Explain in plain language what the weakest barrier means for this risk, and why strengthening it specifically
(rather than adding more unrelated controls) is the highest-priority action."""
    return chat_completion(SYSTEM_PROMPT, prompt)
