# منصة مدارك - Phase 1-I1 Image OCR Intake

منصة مدارك هي منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.

## حالة هذه الحزمة

```text
Phase 1-I1: Image OCR Intake
الحالة: جاهزة للرفع والاختبار عبر GitHub Actions
```

## ما تضيفه Phase 1-I1

- دعم رفع صورة سؤال/ورقة بصيغ PNG وJPG/JPEG وWEBP.
- تشغيل OCR إنجليزي مبدئي على الصورة باستخدام Tesseract.
- حفظ النص المستخرج من الصورة داخل جلسة المشروع المؤقتة.
- عرض مقتطف النص المستخرج في خطوة استخراج الأسئلة.
- استخدام النص المستخرج من الصورة في مسار تقسيم الأسئلة الحالي.
- إبقاء دعم PDF النصي السابق كما هو.
- تحديث GitHub Actions لتثبيت `tesseract-ocr` و`tesseract-ocr-eng` قبل اختبارات Backend.
- اختبارات Backend جديدة لمسار OCR.

## المسار الحالي

```text
رفع PDF نصي أو صورة واضحة
→ استخراج النص مباشرة من PDF أو عبر OCR للصورة
→ تقسيم النص إلى بطاقات أسئلة
→ توليد قاموس مصطلحات أولي
→ ترجمة أولية عبر طبقة مزود آمنة
→ مراجعة وتعديل وحذف وترتيب
→ ربط صور/جداول يدوية بالأسئلة
→ تصدير DOCX/PDF بتنسيق RTL مع الشعار والمرفقات
```

## ما لا يدخل في هذه المرحلة

- لا OCR كامل لـ PDF المصوّر متعدد الصفحات.
- لا تحليل تخطيط تلقائي للرسوم والجداول من PDF.
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

> ملاحظة: OCR يحتاج وجود Tesseract في بيئة التشغيل. GitHub Actions يثبته تلقائيًا في هذه المرحلة.

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
