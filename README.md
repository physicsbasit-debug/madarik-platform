# منصة مدارك - Phase 1-F1 DOCX Export RTL

هذه الحزمة تمثل نقطة تطوير **Phase 1-F1** بعد نجاح Phase 1-E2.

هدف المرحلة: إضافة تصدير Word حقيقي بصيغة DOCX وبتنسيق عربي RTL، مع بقاء PDF مؤجلًا لمرحلة مستقلة. نعم، لم نفتح معركة PDF العربي الآن، لأننا بشر عقلاء أحيانًا.

## ماذا أضافت Phase 1-F1؟

- خدمة Backend للتصدير:
  - `backend/app/services/export.py`
- Endpoint جديد:
  - `POST /api/projects/{project_id}/export/docx`
- إنشاء ملف DOCX حقيقي من الأسئلة النشطة غير المحذوفة.
- دعم النسخة العربية النظيفة والنسخة الثنائية اللغة حسب إعدادات المشروع.
- رأس ورقة RTL يحتوي بيانات المدرسة والمادة والصف والزمن والدرجة والمعلم والتاريخ.
- إعادة ترقيم الأسئلة تلقائيًا حسب ترتيب المعلم.
- حذف الأسئلة ذات الحالة `deleted` من الملف النهائي.
- زر تحميل Word في خطوة التصدير.
- اختبارات Backend للتحقق من إنشاء DOCX وتحميله من API.

## ما لا يزال مؤجلًا

- تصدير PDF الحقيقي.
- إدراج الصور والجداول داخل DOCX.
- شعار المدرسة في الرأس.
- OCR للصور وPDF الممسوح ضوئيًا.
- الترجمة عبر AI خارجي.
- نموذج الإجابة والتحليل المتقدم.
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

تُقبل Phase 1-F1 إذا:

- GitHub Actions أخضر.
- Backend checks ناجحة.
- Frontend build ناجح.
- يمكن إنشاء DOCX من مشروع يحتوي أسئلة نشطة.
- لا تظهر الأسئلة المحذوفة في ملف Word.
- يدعم التصدير النسخة العربية والثنائية.
- لا يدخل PDF أو OCR أو AI خارجي في هذه المرحلة.
