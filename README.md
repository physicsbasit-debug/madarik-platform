# منصة مدارك

منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى نسخ عربية أو ثنائية اللغة قابلة للمراجعة والتدقيق والتصدير بصيغ مناسبة للطباعة.

## الحالة الحالية

- الإصدار البرمجي: `2.0.0-rc.1`
- آخر مرحلة مدمجة: `Phase 4-B1: Real AI Translation Acceptance`
- الحالة التقنية: ناجحة في الاختبارات والبناء
- القبول الإنتاجي النهائي: معلّق حتى نجاح ترجمة ورقة Cambridge كاملة باستخدام مزود ذكاء اصطناعي حقيقي
- المرحلة التالية: `Final Release Candidate`

### خط الأساس المختبر

- اختبارات Phase 4-B1 المركزة: `58 passed`
- اختبارات Backend الكاملة: `245 passed`
- Frontend lint: ناجح
- Frontend production build: ناجح
- بوابة Phase 4-B1: ناجحة

> نجاح الاختبارات التقنية لا يعني اكتمال القبول الإنتاجي. يجب التأكد من أن الترجمة ناتجة من مزود خارجي حقيقي وليست من مسار `fallback`.

## ماذا تفعل المنصة؟

تدعم منصة مدارك رحلة معالجة الورقة التعليمية من الملف الأصلي إلى نسخة عربية قابلة للمراجعة والتصدير:

```text
إنشاء مشروع
→ رفع PDF أو صورة
→ استخراج النص أو تشغيل OCR
→ تقسيم الورقة إلى أسئلة وأجزاء
→ مراجعة بنية الأسئلة والدرجات
→ استخراج وربط وقص الرسوم والجداول
→ توليد قاموس مصطلحات
→ ترجمة تعليمية أولية
→ مراجعة اللغة والرموز العلمية
→ اعتماد الأسئلة
→ فحص جاهزية التصدير
→ تصدير DOCX وPDF
```

## الوظائف الرئيسية

- رفع ملفات PDF والصور التعليمية.
- استخراج النص من PDF النصي.
- تشغيل OCR على الصور والملفات المصورة المدعومة.
- تقسيم النص إلى أسئلة وأجزاء وخيارات.
- دعم الأسئلة متعددة الأجزاء.
- ربط الأصول البصرية بالأسئلة.
- قص الرسوم والجداول من صفحات PDF.
- إنشاء قاموس مصطلحات ومراجعته.
- دعم الترجمة عبر:
  - Gemini `generateContent`
  - OpenAI Responses API
  - مزودات OpenAI-compatible
- استخدام fallback محلي واضح عند تعذر المزود الخارجي.
- منع اعتماد ترجمة fallback بوصفها ترجمة نهائية.
- فحص جودة اللغة العربية وبقايا النثر الإنجليزي.
- حماية الرموز والقيم والوحدات والمعادلات العلمية.
- محاولة تصحيح خارجية واحدة عند اكتشاف مخالفة.
- مراجعة الأسئلة وتعديلها وحذفها واستعادتها وترتيبها.
- إجراءات جماعية لحالات المراجعة.
- فحص جاهزية التصدير وموانع القبول.
- تصدير نسخ الطالب بصيغتي DOCX وPDF مع RTL.
- حفظ المشاريع في SQLite.
- تصدير واستيراد Snapshot بصيغة JSON.
- حسابات مستخدمين وأدوار وصلاحيات أولية.
- أدوات تحليل تربوي وجودة تعليمية.

## معايير الترجمة العلمية

يسمح حارس الجودة بالرموز والمصطلحات العلمية الضرورية مثل:

```text
V = IR
I = 2 A
5 Ω
CMBR
Fig. 1.1
5.0 × 10⁻⁴
```

ويرفض النصوص المختلطة غير المفسرة مثل:

```text
فسّر why the current decreases
```

كما يتحقق مسار القبول من:

- سلامة القيم الرقمية.
- سلامة الوحدات والرموز.
- سلامة الدرجات.
- احترام القاموس المعتمد.
- عدم اعتماد ترجمة fallback.
- تسجيل مصدر الترجمة الخارجي عند نجاح المزود.

## التقنيات المستخدمة

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- PyMuPDF
- pypdf
- Tesseract OCR
- python-docx
- ReportLab
- httpx
- pytest

### Frontend

- React
- TypeScript
- Vite
- ESLint
- Lucide React

## بنية المشروع

```text
madarik-platform/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
├── RUN_PHASE4_B1_TESTS.sh
├── RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
└── README.md
```

## تشغيل Backend

من جذر المشروع:

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

على Windows:

```powershell
cd backend

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> يحتاج OCR إلى تثبيت Tesseract في نظام التشغيل، وليس داخل بيئة Python فقط.

## تشغيل Frontend

من جذر المشروع:

```bash
cd frontend

npm ci
npm run dev -- --host 0.0.0.0
```

لإنشاء نسخة إنتاج:

```bash
cd frontend

npm run lint
npm run build
```

## إعداد مزود الذكاء الاصطناعي

انسخ ملف البيئة النموذجي:

```bash
cd backend

cp .env.example .env
```

ثم أدخل داخل `backend/.env`:

- اسم المزود.
- مفتاح API صالح.
- معرّف نموذج مدعوم حاليًا من المزود.
- عنوان API عند الحاجة.

راجع الملف:

```text
backend/.env.example
```

### قواعد أمنية

- لا تحفظ مفاتيح API داخل Git.
- لا ترسل المفتاح في المحادثات أو السجلات.
- لا تستخدم اسم نموذج تخمينيًا.
- لا تعتمد نتيجة fallback بوصفها ترجمة خارجية.
- لا تطبع الاستجابة الخام في الاختبار الحي.

## الاختبارات

### بوابة Phase 4-B1

من جذر المشروع:

```bash
chmod +x RUN_PHASE4_B1_TESTS.sh
./RUN_PHASE4_B1_TESTS.sh
```

تشمل البوابة:

- فحص Python syntax.
- اختبارات Backend المركزة.
- Frontend lint.
- Frontend production build.

### اختبارات Backend الكاملة

```bash
cd backend

source .venv/bin/activate
python -m pytest -q
```

### الاختبار الحي

بعد إعداد مزود ومفتاح ونموذج صالحين:

```bash
cd /path/to/madarik-platform

source backend/.venv/bin/activate

python RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
```

الاختبار الحي لا يطبع المفتاح أو الحمولة السرية.

## بوابة القبول الإنتاجي

لا تعد Phase 4-B1 مغلقة إنتاجيًا إلا بعد تحقق جميع الشروط التالية:

- استخدام مزود ذكاء اصطناعي خارجي حقيقي.
- ترجمة ورقة Cambridge كاملة.
- التأكد من أن الناتج ليس fallback.
- عدم بقاء نثر إنجليزي غير مفسر في النسخة العربية.
- سلامة القيم والرموز والوحدات والأسس العلمية.
- سلامة الرسوم والأصول البصرية في DOCX وPDF.
- اتساق الدرجات وسياسة العلامات.
- اجتياز مراجعة المعلم.
- وصول تقرير الرحلة الكاملة إلى حالة قبول صحيحة.

## الحالة غير المنجزة

- الاختبار الحي الكامل يحتاج مفتاح API وموديلًا صالحين.
- القبول النهائي لورقة Cambridge الكاملة لم يُغلق بعد.
- المشروع لم يُعلن نسخة إنتاج نهائية.
- المرحلة المتبقية بعد القبول الحي هي `Final Release Candidate`.

## الوثائق

توجد وثائق المراحل والقبول داخل مجلد:

```text
docs/
```

وثيقة Phase 4-B1 الأساسية:

```text
docs/PHASE_4_B1_REAL_AI_TRANSLATION_ACCEPTANCE.md
```

## ملاحظة التطوير

يجب أن تمر التعديلات الجديدة عبر الاختبارات المركزة والاختبارات الكاملة وبناء الواجهة قبل الدمج. أي تحسين لا يدخل في نطاق الإغلاق الحالي يُرحّل إلى إصدار لاحق بدل توسيع النسخة المرشحة بلا نهاية.

## Madarik Science Platform V2 Status

Development branch:

```text
feat/madarik-science-platform-v2
```

Completed V2 phases:

- Phase 0-A through Phase 6-A.
- Phase 6-B: Automatic Question Selection and Blueprint Validation.

Automatic selection uses grade, science domain, unit, and cognitive category. It reports shortages instead of silently substituting unclassified questions. Validation checks question count, total marks, cognitive distribution, and unclassified items.

Next planned phase:

```text
Phase 6-C: Assessment Ordering, Sections, and Manual Marks
```

