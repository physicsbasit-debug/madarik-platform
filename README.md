# منصة مدارك - Phase 1-F2 PDF Export RTL

منصة مدارك هي منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.

## حالة هذه الحزمة

هذه الحزمة تمثل مرحلة:

```text
Phase 1-F2: PDF Export RTL
```

تتضمن هذه المرحلة:

- رفع PDF نصي واستخراج النص.
- تحويل النص المستخرج إلى بطاقات أسئلة.
- توليد قاموس مصطلحات أولي.
- ترجمة أولية محافظة قابلة للمراجعة.
- مراجعة الأسئلة وتعديلها وحذفها وترتيبها.
- تصدير DOCX فعلي بتنسيق RTL.
- تصدير PDF فعلي بتنسيق RTL أولي.

## ما لا يدخل في هذه المرحلة

- لا OCR.
- لا AI خارجي فعلي.
- لا نموذج إجابة.
- لا تصدير صور وجداول داخل PDF/Word بعد.
- لا شعار مدرسة داخل التصدير بعد.
- لا حفظ دائم للمشاريع.
- لا حسابات مستخدمين.

## تشغيل Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

على Windows:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## تشغيل Frontend

```bash
cd frontend
npm install
npm run dev
```

## الفحص

```bash
cd backend
pytest -q
```

```bash
cd frontend
npm run build
```

## Endpoints مهمة

```text
GET  /api/health
POST /api/projects
POST /api/projects/{project_id}/upload-pdf
POST /api/projects/{project_id}/parse-questions
POST /api/projects/{project_id}/glossary/generate
POST /api/projects/{project_id}/translate-questions
POST /api/projects/{project_id}/export/docx
POST /api/projects/{project_id}/export/pdf
```

## ملاحظة PDF

تصدير PDF في هذه المرحلة أولي ومحافظ:

- يدعم RTL باستخدام ReportLab مع تشكيل عربي عبر `arabic-reshaper` و`python-bidi`.
- يعتمد على خط Unicode متاح في النظام مثل DejaVu Sans.
- لا يترجم النص داخل الصور ولا يدرج الرسوم والجداول بعد.

## نقطة الاستقرار السابقة

- Phase 0 Skeleton ✅
- Phase 1-A Static UI ✅
- Phase 1-B Backend API Integration ✅
- Phase 1-C PDF Text Extraction ✅
- Phase 1-D Question Parser ✅
- Phase 1-E1 Glossary Engine ✅
- Phase 1-E2 Translation Engine ✅
- Phase 1-F1 DOCX Export RTL ✅
- Phase 1-F2 PDF Export RTL ⏳
