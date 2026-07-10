# منصة مدارك - Phase 1-C PDF Text Extraction

هذه الحزمة تمثل نقطة تطوير **Phase 1-C** لمنصة مدارك بعد نجاح Phase 1-B.

الهدف في هذه المرحلة بسيط ومحدد: **رفع ملف PDF نصي حقيقي واستخراج النص الخام منه عبر FastAPI**، دون OCR ودون ترجمة ودون تصدير فعلي. خطوة صغيرة، لكنها تمنعنا من بناء قلعة فوق ملف لا نعرف قراءته أصلًا، وهذا شيء يبدو بديهيًا لكن البشرية تجاهلته كثيرًا.

## ماذا أضافت Phase 1-C؟

- دعم رفع PDF حقيقي من الواجهة.
- Endpoint جديد في Backend:
  - `POST /api/projects/{project_id}/upload-pdf`
- استخراج النص من PDF نصي باستخدام `pypdf`.
- حفظ نتيجة الاستخراج داخل جلسة المشروع المؤقتة.
- عرض حالة الاستخراج في الواجهة.
- عرض مقتطف النص المستخرج في خطوة استخراج الأسئلة.
- رسالة واضحة إذا كان PDF مصوّرًا أو لا يحتوي على نص قابل للاستخراج.
- اختبارات Backend لاستخراج النص ورفع PDF.
- بقاء الأسئلة والقاموس تجريبيين كما هما، لأن تقسيم الأسئلة الحقيقي مؤجل إلى Phase 1-D.

## ما لا يزال مؤجلًا

- OCR للصور وPDF الممسوح ضوئيًا.
- تقسيم الأسئلة من النص الحقيقي.
- استخراج المصطلحات الحقيقي.
- الترجمة عبر AI.
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

تُقبل Phase 1-C إذا:

- GitHub Actions أخضر.
- Backend checks ناجحة.
- Frontend build ناجح.
- PDF نصي يرفع بنجاح ويستخرج نصًا.
- PDF بلا نص يرجع رسالة واضحة بأن OCR مؤجل.
- لا تدخل OCR أو AI أو Export فعلي.
- لا تنكسر واجهة RTL أو مزامنة Backend من Phase 1-B.
