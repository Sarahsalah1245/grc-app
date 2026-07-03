"""
Groq Client
===========
بنستخدم Groq (https://console.groq.com) لأنه:
1. بيدي API key مجاني بحد استخدام يومي سخي (كفاية لمشروع تخرج/هاكاثون وحتى مستخدمين حقيقيين بعدد محدود).
2. الاستدلال (inference) بيحصل على سيرفراتهم مش على جهاز المستخدم -> مفيش حاجة محتاجة جهاز قوي.
3. بيدعم نماذج Llama مفتوحة المصدر بسرعة عالية جدًا.

لو عايزة بديل لما تكبر المشروع: Google Gemini API (فيه free tier كمان بحدود مختلفة).
الكود هنا مكتوب بحيث لو غيّرتي المزوّد، بس تغيّري الملف ده وكل حاجة تانية تفضل شغالة.
"""

from groq import Groq
from app.config import settings

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY مش موجود في الـ .env - اعملي حساب مجاني في console.groq.com")
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 800) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
