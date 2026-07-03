"""
COBIT Mapping (Lightweight RAG)
================================
بدل ما نستخدم Vector Database (اللي محتاج تشغيل ومصاريف إضافية)، بنعمل RAG
مبسّط كفاية جدًا لحجم البيانات ده (18 objective بس):

1. Retrieval: بنفلتر أهداف COBIT اللي فيها keywords قريبة من وصف الخطر (بحث نصي بسيط).
2. Augmentation: بنحط الأهداف المرشحة دي جوه الـ prompt.
3. Generation: الـ LLM يختار الأنسب منها فعليًا ويشرح ليه، من غير ما "يخترع" objective ID مش موجود أصلاً.

الطريقة دي كافية جدًا لعدد صغير من المستندات. لو المشروع كبر (مثلاً ضفتي
كل تفاصيل COBIT الرسمية بمئات الصفحات) وقتها هيبقى محتاج pgvector فعلي
على Supabase (مجاني برضو ومتاح كـ extension).
"""

import json
from pathlib import Path
from app.llm.groq_client import chat_completion

_DATA_PATH = Path(__file__).parent.parent / "data" / "cobit_2019.json"
_COBIT_OBJECTIVES = json.loads(_DATA_PATH.read_text(encoding="utf-8"))

SYSTEM_PROMPT = """You are a certified COBIT 2019 expert. Your job is to map a given risk
description to the appropriate governance/management objectives from the provided list only -
never invent an objective ID that is not in the list. Return your answer as JSON ONLY in the
following format with no extra text:
{"selected": [{"id": "APO12", "reason": "short reason"}], "summary": "one-line overall summary"}"""


def _keyword_shortlist(risk_text: str, top_n: int = 8) -> list[dict]:
    text_lower = risk_text.lower()
    scored = []
    for obj in _COBIT_OBJECTIVES:
        score = sum(1 for kw in obj["keywords"] if kw.lower() in text_lower)
        if score > 0:
            scored.append((score, obj))
    scored.sort(key=lambda x: x[0], reverse=True)
    shortlist = [obj for _, obj in scored[:top_n]]
    # لو مفيش أي تطابق keywords، رجّعي القائمة كاملة (المشروع صغير أصلًا فمش هيثقل على الـ LLM)
    return shortlist if shortlist else _COBIT_OBJECTIVES


def map_risk_to_cobit(risk_description: str) -> dict:
    shortlist = _keyword_shortlist(risk_description)
    candidates_text = "\n".join(
        f"- {o['id']} ({o['domain']}): {o['title']}" for o in shortlist
    )

    prompt = f"""Risk description:
\"\"\"{risk_description}\"\"\"

Candidate objectives from COBIT 2019:
{candidates_text}

Select the most suitable 1-3 objectives from the list above ONLY and return JSON in the required format."""

    raw = chat_completion(SYSTEM_PROMPT, prompt, temperature=0.1)

    try:
        # The model sometimes wraps the JSON in ```json ... ``` so we strip that if present
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        parsed = {"selected": [], "summary": "Could not parse the model's response - please try again.", "raw": raw}

    return parsed
