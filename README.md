# منصة مدارك - Phase 1-E1 Glossary Engine

هذه الحزمة تمثل نقطة تطوير **Phase 1-E1** بعد نجاح Phase 1-D.

هدف المرحلة: توليد قاموس مصطلحات أولي للمعلم من بطاقات الأسئلة، باستخدام محرك داخلي محافظ وقائم على قائمة مصطلحات علمية أولية. لا يوجد AI، ولا OCR، ولا ترجمة فعلية، ولا تصدير DOCX/PDF فعلي بعد. نعم، ما زلنا نمنع المشروع من لبس عباءة الذكاء الخارق قبل أن يتعلم الوقوف بثبات.

## ماذا أضافت Phase 1-E1؟

- خدمة Backend جديدة/مفعّلة:
  - `backend/app/services/glossary.py`
- Endpoint جديد:
  - `POST /api/projects/{project_id}/glossary/generate`
- زر في خطوة قاموس الورقة:
  - **توليد قاموس من الأسئلة**
- استخراج مصطلحات علمية من بطاقات الأسئلة الناتجة عن Phase 1-D.
- استخدام قائمة مصطلحات أولية في العلوم والفيزياء والكيمياء والأحياء.
- إنشاء مصطلحات بحالة `needs_review` حتى يراجعها المعلم قبل الترجمة.
- استمرار إمكانية تعديل الترجمة العربية للمصطلح وحالته.
- تحديث اختبارات Backend.
- تحديث الواجهة لتعرض أن القاموس المستخرج للمعلم فقط.

## ما لا يزال مؤجلًا

- الترجمة عبر AI.
- استخدام القاموس في ترجمة الأسئلة.
- OCR للصور وPDF الممسوح ضوئيًا.
- ربط الصور والجداول بالسؤال.
- التصدير الحقيقي إلى DOCX/PDF.
- حفظ قاموس المدرسة بشكل دائم.
- الحسابات والصلاحيات.

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

تُقبل Phase 1-E1 إذا:

- GitHub Actions أخضر.
- Backend checks ناجحة.
- Frontend build ناجح.
- النص المستخرج يتحول إلى بطاقات أسئلة كما في Phase 1-D.
- يمكن توليد قاموس مصطلحات من بطاقات الأسئلة.
- تظهر المصطلحات في شاشة قاموس الورقة.
- يمكن تعديل المصطلحات وحالتها.
- لا تدخل ترجمة AI أو OCR أو Export فعلي.
- لا تنكسر واجهة RTL أو مزامنة Backend من المراحل السابقة.
