# GRC Risk Intelligence Platform

منصة تقييم مخاطر (GRC) بتجمع بين:
- تقييم **نوعي** (Qualitative) - مصفوفة احتمالية × تأثير
- تقييم **كمي** (Quantitative) - SLE / ALE / ROSI
- **محاكاة مونت كارلو** (أسلوب FAIR) لتوزيع احتمالي كامل للخسارة السنوية
- **FMEA** (Failure Mode and Effects Analysis) - ترتيب أولويات المخاطر عن طريق RPN = Severity × Occurrence × Detection
- **Bow-Tie Analysis** - تحليل بصري بيربط أسباب الخطر بنتائجه عن طريق ضوابط وقائية وتخفيفية (barrier-based)
- **تحليل SWOT** مع تحويل التهديدات/نقاط الضعف لبنود مخاطر رسمية
- **ربط تلقائي بمعيار COBIT 2019** عن طريق RAG خفيف + LLM
- **شرح بالذكاء الاصطناعي (XAI)** لكل نتيجة حسابية - الأرقام كلها بتتحسب رياضيًا (مش الـ AI هو اللي بيخترعها)، ودور الـ LLM بس إنه يشرحها

> **ملحوظة:** واجهة التطبيق (Frontend) وكل ردود الذكاء الاصطناعي كلها بالإنجليزي بالكامل. الشرح ده (الـ README) بالعربي بس عشان يسهّل عليكِ المتابعة والفهم.

---

## 1) البنية التقنية (Architecture)

```
المستخدم → Frontend (React/Vite على Vercel)
              ↓  HTTPS + JWT
          Backend (FastAPI على Render)
              ↓                    ↓
     PostgreSQL (Supabase)     Groq API (LLM مجاني)
```

| الطبقة | التقنية | ليه اخترناها |
|---|---|---|
| Frontend | React + Vite | خفيف، سريع البناء، ودعم ممتاز لـ Vercel المجاني |
| Backend | FastAPI (Python) | سريع، Type-safe، وده اللي بيحسب كل الأرقام (مش الـ AI) |
| Database | PostgreSQL عبر Supabase | مجاني، فيه Row Level Security جاهز، ومناسب لبيانات GRC الحساسة |
| LLM | Groq API (نموذج Llama مفتوح المصدر) | مجاني 100% للمستخدم، الاستدلال بيحصل على سيرفرات Groq مش على جهازك، فمحتاجاش جهاز قوي |

---

## 2) ليه الاختيارات دي بالذات؟ (مهم تفهميها مش بس تنفذيها)

### قاعدة البيانات ولية Supabase؟
- Supabase = PostgreSQL مُدار + طبقة أمان جاهزة (Row Level Security) + مجاني لحد 500MB (كفاية جدًا لمرحلة المشروع/الهاكاثون).
- الأمان بيتحقق بثلاث طبقات:
  1. **كلمات المرور**: بتتخزن مشفرة بـ bcrypt (مش نص عادي أبدًا) - شوفي `backend/app/auth.py`.
  2. **JWT Tokens**: كل طلب API لازم يبقى معاه توكن صالح، وده بيمنع أي حد يشوف بيانات مش بتاعته.
  3. **Row Level Security (تفعليها من Supabase Dashboard)**: تضمن إن أي منظمة تشوف بيانات مخاطرها بس، مش بيانات منظمات تانية على نفس القاعدة.
- **قاعدة ذهبية**: متحطيش أي مفتاح أو باسورد في الكود نفسه - كله في ملف `.env` (اللي مش بيترفع على GitHub خالص، شوفي `.gitignore`).

### LLM ولية Groq؟
- طلبك كان: مجاني 100% للمستخدمين + بلاش جهاز قوي. الحل الوحيد اللي يحقق الاتنين مع بعض هو **API مجاني** (مش تشغيل نموذج على جهازك)، لأن أي نموذج تشغليه محليًا (Ollama مثلاً) هيحتاج GPU قوي.
- Groq بيدي مفتاح API مجاني بحد استخدام يومي سخي، وسرعته عالية جدًا مقارنة بمنافسين تانيين.
- الكود مبني بحيث لو حبيتي تغيّري لـ Google Gemini API (بديل مجاني كمان) مستقبلًا، هتغيّري ملف واحد بس: `backend/app/llm/groq_client.py`.

### ليه الـ AI مش بيحسب الأرقام؟ (نقطة أمان جوهرية)
كل حسابات المخاطر (qualitative, ALE, Monte Carlo) بتتم بكود Python رياضي عادي (`backend/app/risk_engine/`) - مفيش أي احتمال "هلوسة" فيها. دور الـ LLM محصور في **شرح** الأرقام دي بلغة بسيطة، مش توليدها. ده بالظبط الحل لمشكلة الـ Hallucination اللي كانت مذكورة في التحليل الأول بتاعك.

---

## 3) خطوات التشغيل محليًا (قبل الرفع على الكلاود)

### أ) الباك اند
```bash
cd backend
python -m venv venv
source venv/bin/activate      # على ويندوز: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# افتحي .env واملي القيم (DATABASE_URL مؤقتًا ممكن تخليها sqlite:///./dev.db للتجربة المحلية)

uvicorn app.main:app --reload --port 8000
```
افتحي `http://localhost:8000/docs` وهتلاقي Swagger UI بيوثّق كل الـ endpoints تلقائيًا.

### ب) الفرونت اند
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
افتحي `http://localhost:5173`

---

## 4) الرفع على الكلاود المجاني (خطوة بخطوة)

### الخطوة 1: قاعدة البيانات - Supabase (مجاني)
1. سجّلي في https://supabase.com بحساب GitHub.
2. "New Project" → اختاري اسم وباسورد قوي لقاعدة البيانات (احفظيه، هتحتاجيه بعدين).
3. من `Project Settings → Database → Connection String` انسخي الـ URI (اختاري وضع "Session pooler" أو "Transaction pooler" لأداء أفضل مع Render).
4. **فعّلي الأمان**: من `Authentication → Policies` فعّلي Row Level Security على الجداول بعد أول تشغيل للباك اند (اللي بينشئ الجداول تلقائيًا).

### الخطوة 2: مفتاح الـ LLM - Groq (مجاني)
1. سجّلي في https://console.groq.com
2. `API Keys → Create API Key` وانسخيه.

### الخطوة 3: الباك اند - Render (مجاني)
1. ارفعي مجلد `backend` على مستودع GitHub منفصل (أو جزء من مستودع واحد للمشروع كله).
2. سجّلي في https://render.com بحساب GitHub.
3. `New → Web Service` → اختاري المستودع.
4. الإعدادات:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
5. من `Environment` ضيفي كل المتغيرات اللي في `.env.example` بقيمها الحقيقية (DATABASE_URL من Supabase، GROQ_API_KEY من Groq، JWT_SECRET_KEY ولّديها بالأمر: `python -c "import secrets; print(secrets.token_hex(32))"`).
6. Deploy. هتاخدي رابط زي `https://your-app.onrender.com`.
   > ملحوظة: الخطة المجانية في Render بتنام بعد فترة عدم استخدام، وأول طلب بعد النوم بياخد شوية ثواني إضافية - ده طبيعي في الخطة المجانية.

### الخطوة 4: الفرونت اند - Vercel (مجاني)
1. ارفعي مجلد `frontend` على GitHub.
2. سجّلي في https://vercel.com بحساب GitHub.
3. `Add New → Project` → اختاري المستودع.
4. Framework Preset: Vite (بيتعرف تلقائيًا).
5. من `Environment Variables` ضيفي: `VITE_API_URL` = رابط الباك اند من Render.
6. Deploy. هتاخدي رابط زي `https://your-app.vercel.app`.

### الخطوة 5: اربطي الاتجاهين ببعض
- ارجعي لـ Render وحدّثي متغير `FRONTEND_ORIGIN` بيبقى رابط Vercel بتاعك (عشان الـ CORS يسمح بيه بس).
- جربي تسجّلي حساب من على رابط Vercel وشوفي إنه بيتواصل مع الباك اند صح.

---

## 5) خريطة الـ API (لما تفتحي `/docs`)

| Method | Endpoint | الوظيفة |
|---|---|---|
| POST | `/auth/register` | تسجيل حساب جديد |
| POST | `/auth/login` | تسجيل الدخول |
| POST | `/risks/qualitative/explain` | تقييم نوعي + شرح AI |
| POST | `/risks/quantitative/explain` | تقييم كمي (ALE) + شرح AI |
| POST | `/risks/monte-carlo/explain` | محاكاة مونت كارلو + شرح AI |
| POST | `/risks/rosi` | حساب عائد الاستثمار الأمني |
| POST | `/risks/full-analysis` | تحليل شامل (الكل مع بعض + COBIT) |
| POST | `/swot/analyze` | تحليل SWOT |
| GET | `/cobit/objectives` | كل أهداف COBIT 2019 المتاحة |
| POST | `/cobit/map` | ربط وصف خطر بأهداف COBIT مناسبة |

---

## 6) خطوات تالية مقترحة (لما يبقى عندك وقت)

1. **تفعيل Row Level Security فعليًا على Supabase** بحيث كل منظمة تشوف بياناتها بس (دلوقتي الفلترة بتتم على مستوى الكود، وده كافي للمرحلة دي بس RLS بيديك طبقة حماية إضافية على مستوى القاعدة نفسها).
2. **تسجيل نتائج التحليلات في الداتابيز** (دلوقتي الـ endpoints بترجع النتيجة مباشرة من غير ما تتخزن - ضيفي router بيحفظ في جدول `risk_items` عشان يبقى عندك تاريخ وتقارير).
3. **صفحة Dashboard** بترسم كل الـ risk items المتخزنة على heat map واحدة.
4. **توسيع بيانات COBIT** - الملف الحالي فيه 18 objective رئيسي كبداية؛ ممكن تضيفي التفاصيل الكاملة (Governance/Management Practices) من الوثيقة الرسمية.
5. **كتابة الـ Research Paper** بالتوازي - وثّقي منهجية الـ Monte Carlo والـ RAG بتاعتك، ده بالظبط الجزء اللي هيميزك أكاديميًا.
