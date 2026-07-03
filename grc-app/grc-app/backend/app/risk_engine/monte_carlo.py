"""
Monte Carlo Simulation Engine
==============================
المشكلة في الحساب العادي (SLE/ALE): بيفترض إن كل حاجة رقم ثابت، لكن الواقع
مليان عدم يقين (uncertainty). هنا بنقول بدل الرقم الثابت "هيحصل 3 مرات في
السنة بخسارة 100,000 جنيه"، بنقول "هيحصل ما بين 1 و5 مرات، والخسارة ما بين
50,000 و 300,000"، وبنعمل آلاف السيناريوهات العشوائية عشان نشوف التوزيع
الاحتمالي الكامل للخطر. ده أسلوب الـ FAIR (Factor Analysis of Information Risk)
اللي بيستخدموه في البنوك الكبيرة.

المدخلات (لكل عامل بتدّي أقل قيمة / الأرجح / أعلى قيمة -> توزيع PERT/Triangular):
- frequency: عدد مرات الحدوث المتوقعة في السنة (min, most_likely, max)
- magnitude: قيمة الخسارة لو حصلت الحادثة (min, most_likely, max)

المخرجات:
- توزيع احتمالي كامل للخسارة السنوية (annual loss)
- Value at Risk (VaR) عند 95% و99% -> "احنا واثقين 95% إن خسارتنا السنوية مش هتتخطى X"
- مؤشرات وصفية: mean, median, percentiles
- بيانات histogram جاهزة للرسم في الفرونت اند
"""

import numpy as np


def _pert_sample(min_val: float, most_likely: float, max_val: float, size: int, rng) -> np.ndarray:
    """
    توزيع PERT (نسخة معدّلة من Beta distribution) - بيُستخدم لما تقدري تحطي
    (أقل قيمة، القيمة الأرجح، أعلى قيمة) بدل التوزيع الطبيعي البسيط، وهو
    الأنسب لتقديرات الخبراء البشرية في تحليل المخاطر.
    """
    if min_val > most_likely or most_likely > max_val:
        raise ValueError("must satisfy: min <= most_likely <= max")
    if min_val == max_val:
        return np.full(size, min_val)

    lam = 4.0  # shape parameter القياسي لـ PERT
    alpha = 1 + lam * (most_likely - min_val) / (max_val - min_val)
    beta = 1 + lam * (max_val - most_likely) / (max_val - min_val)
    sample = rng.beta(alpha, beta, size)
    return min_val + sample * (max_val - min_val)


def run_monte_carlo_simulation(
    freq_min: float, freq_most_likely: float, freq_max: float,
    mag_min: float, mag_most_likely: float, mag_max: float,
    iterations: int = 10000,
    seed: int | None = None,
) -> dict:
    """
    بتشغّل محاكاة مونت كارلو لتقدير الخسارة السنوية المحتملة لخطر معين.
    كل iteration = سيناريو "سنة كاملة" افتراضية.
    """
    rng = np.random.default_rng(seed)

    # 1) لكل سيناريو، نحدد كام مرة الحادثة هتحصل في السنة دي (توزيع منفصل تقريبي عن طريق PERT + تقريب)
    frequencies = _pert_sample(freq_min, freq_most_likely, freq_max, iterations, rng)
    occurrences = np.round(frequencies).astype(int)
    occurrences = np.clip(occurrences, 0, None)

    # 2) لكل حادثة فعلية بتحصل، نولّد قيمة خسارة عشوائية من توزيع الـ magnitude
    annual_losses = np.zeros(iterations)
    max_occurrences = int(occurrences.max()) if len(occurrences) else 0
    if max_occurrences > 0:
        # نولّد مصفوفة خسائر كبيرة مرة واحدة بدل loop عشان الأداء
        all_magnitudes = _pert_sample(mag_min, mag_most_likely, mag_max,
                                       iterations * max_occurrences, rng).reshape(iterations, max_occurrences)
        for i in range(iterations):
            n = occurrences[i]
            if n > 0:
                annual_losses[i] = all_magnitudes[i, :n].sum()

    percentiles = {
        "p10": float(np.percentile(annual_losses, 10)),
        "p50": float(np.percentile(annual_losses, 50)),
        "p90": float(np.percentile(annual_losses, 90)),
        "p95": float(np.percentile(annual_losses, 95)),
        "p99": float(np.percentile(annual_losses, 99)),
    }

    hist_counts, hist_edges = np.histogram(annual_losses, bins=20)

    return {
        "iterations": iterations,
        "mean_annual_loss": round(float(np.mean(annual_losses)), 2),
        "median_annual_loss": round(percentiles["p50"], 2),
        "std_dev": round(float(np.std(annual_losses)), 2),
        "min_loss": round(float(np.min(annual_losses)), 2),
        "max_loss": round(float(np.max(annual_losses)), 2),
        "percentiles": {k: round(v, 2) for k, v in percentiles.items()},
        "value_at_risk_95": round(percentiles["p95"], 2),
        "value_at_risk_99": round(percentiles["p99"], 2),
        "histogram": {
            "counts": hist_counts.tolist(),
            "bin_edges": [round(e, 2) for e in hist_edges.tolist()],
        },
    }
