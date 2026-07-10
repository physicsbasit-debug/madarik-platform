# منصة مدارك - Phase 1-H1 Question Assets

منصة مدارك هي منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.

## حالة هذه الحزمة

```text
Phase 1-H1: Question Assets
الحالة: جاهزة للرفع والاختبار عبر GitHub Actions
```

## ما تضيفه Phase 1-H1

- ربط صورة أو جدول يدويًا بكل بطاقة سؤال من شاشة المراجعة.
- دعم ملفات PNG وJPG/JPEG لمرفقات السؤال.
- معاينة المرفقات داخل بطاقة السؤال.
- حذف مرفق السؤال من الجلسة المؤقتة.
- إدراج مرفقات الأسئلة في تصدير DOCX.
- إدراج مرفقات الأسئلة في تصدير PDF.
- إبقاء التخزين مؤقتًا داخل جلسة المشروع فقط.
- اختبارات Backend لمسارات رفع/حذف المرفقات وتضمينها في التصدير.

## المسار الحالي

```text
رفع PDF نصي
→ استخراج النص
→ تقسيم النص إلى بطاقات أسئلة
→ توليد قاموس مصطلحات أولي
→ ترجمة أولية عبر طبقة مزود آمنة
→ مراجعة وتعديل وحذف وترتيب
→ ربط صور/جداول يدوية بالأسئلة
→ تصدير DOCX/PDF بتنسيق RTL مع الشعار والمرفقات
```

## ما لا يدخل في هذه المرحلة

- لا OCR.
- لا استخراج تلقائي للصور والجداول من PDF.
- لا ترجمة النصوص داخل الصور.
- لا نموذج إجابة.
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

## فحص المرحلة

```bash
cd backend
pytest -q
```

```bash
cd frontend
npm run build
```
