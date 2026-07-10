# منصة مدارك - Phase 1-D Question Parser

هذه الحزمة تمثل نقطة تطوير **Phase 1-D** بعد نجاح Phase 1-C.

الهدف في هذه المرحلة: تحويل النص المستخرج من PDF نصي إلى **بطاقات أسئلة مستقلة** قابلة للمراجعة، باستخدام قواعد أولية محافظة. لا يوجد OCR، ولا ترجمة AI، ولا تصدير DOCX/PDF فعلي بعد. نعم، ما زلنا نمشي كمهندسين لا كمن يرمي الميزات من فوق السطح.

## ماذا أضافت Phase 1-D؟

- خدمة Backend جديدة:
  - `backend/app/services/question_parser.py`
- Endpoint جديد:
  - `POST /api/projects/{project_id}/parse-questions`
- زر في خطوة استخراج الأسئلة:
  - **تحويل النص إلى بطاقات أسئلة**
- تقسيم النص المستخرج إلى `QuestionItem`.
- التقاط أرقام الأسئلة الشائعة مثل:
  - `1.`
  - `2`
  - `3)`
  - `Question 1:`
- التقاط الدرجات البسيطة مثل:
  - `[2]`
  - `(3 marks)`
  - `1 mark`
- وضع الأسئلة الناتجة بحالة `needs_review` لأن التقسيم آلي أولي ويحتاج مراجعة بشرية.
- بقاء الترجمة مؤجلة إلى Phase 1-E.
- تحديث اختبارات Backend.
- استمرار دعم رفع PDF نصي من Phase 1-C.

## ما لا يزال مؤجلًا

- OCR للصور وPDF الممسوح ضوئيًا.
- الترجمة عبر AI.
- استخراج المصطلحات الحقيقي من النص.
- ربط الصور والجداول بالسؤال.
- التصدير الحقيقي إلى DOCX/PDF.
- الحسابات والصلاحيات.
- حفظ المشاريع دائمًا.

## التشغيل المحلي

### Backend

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

> في التطوير المحلي، يمكن ضبط `VITE_API_BASE_URL=http://127.0.0.1:8000/api` إذا لم تكن الواجهة مخدومة من نفس النطاق.

## الفحص

### Backend

```bash
cd backend
pytest -q
```

### Frontend

```bash
cd frontend
npm run build
```

## نقطة القبول

تُقبل Phase 1-D إذا:

- GitHub Actions أخضر.
- Backend checks ناجحة.
- Frontend build ناجح.
- PDF نصي يرفع ويستخرج نصًا كما في Phase 1-C.
- النص المستخرج يتحول إلى بطاقات أسئلة.
- الأسئلة الناتجة تظهر في شاشة المراجعة.
- الدرجات البسيطة تُلتقط إن ظهرت.
- لا تدخل OCR أو AI أو Export فعلي.
- لا تنكسر واجهة RTL أو مزامنة Backend من المراحل السابقة.
