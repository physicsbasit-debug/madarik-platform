# منصة مدارك - Phase 1-B Backend API Integration

هيكل مشروع **منصة مدارك** بعد تثبيت واجهة Phase 1-A، مع إضافة ربط أولي بين الواجهة وFastAPI في Phase 1-B.

## حالة هذه المرحلة

هذه المرحلة لا تحتوي على OCR أو ترجمة ذكاء اصطناعي أو تصدير DOCX/PDF فعلي. الهدف فقط تثبيت الاتصال بين الواجهة والخلفية عبر جلسة مشروع مؤقتة.

## ماذا أضافت Phase 1-B؟

- إنشاء جلسة مشروع مؤقتة من الواجهة عبر Backend.
- تحميل أسئلة وقاموس تجريبيين من FastAPI بدل الاعتماد الكامل على بيانات داخل الواجهة.
- مزامنة بيانات الورقة مع Backend.
- حفظ معلومات الملف شكليًا في Backend دون رفع الملف الحقيقي.
- مزامنة تعديل بطاقة السؤال.
- مزامنة حذف/استعادة السؤال وتغيير حالته.
- مزامنة إعادة ترتيب الأسئلة.
- مزامنة تعديل قاموس الورقة.
- شريط حالة اتصال يوضح: الاتصال، المزامنة، أو العمل المحلي عند فشل Backend.
- اختبارات Backend موسعة.
- GitHub Actions مستقر على Node 22 وnpm registry العامة.

## ما لا يزال مؤجلًا

- قراءة PDF الحقيقية.
- OCR.
- الترجمة عبر AI.
- استخراج المصطلحات الحقيقي.
- التصدير الحقيقي إلى Word/PDF.
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

> في التطوير المحلي، يمكن ضبط `VITE_API_BASE_URL=http://127.0.0.1:8000/api` إن لم تكن الواجهة مخدومة من نفس النطاق.

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

تُقبل Phase 1-B إذا:

- GitHub Actions أخضر.
- Backend checks ناجحة.
- Frontend build ناجح.
- لا توجد محاولة لإدخال AI/OCR/Export حقيقي.
- الواجهة تبقى RTL.
- تظهر حالة الاتصال بالخلفية.
- يستطيع المستخدم تعديل/حذف/ترتيب الأسئلة مع مزامنة Backend المؤقتة.
