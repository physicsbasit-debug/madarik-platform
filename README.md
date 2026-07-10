# منصة مدارك - Phase 1-G1 AI Provider Layer

منصة مدارك هي منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.

## حالة هذه الحزمة

```text
Phase 1-G1: AI Provider Layer
الحالة: جاهزة للرفع والاختبار عبر GitHub Actions
```

## ما تضيفه Phase 1-G1

- طبقة مزود ترجمة اختيارية داخل Backend.
- بقاء الترجمة التجريبية المحلية `mock` كوضع افتراضي آمن.
- دعم إعداد مزود خارجي لاحقًا عبر متغيرات بيئة فقط، لا من الواجهة.
- fallback تلقائي إذا لم يوجد مفتاح API أو فشل المزود الخارجي.
- endpoint آمن لعرض حالة المزود دون كشف الأسرار.
- تحديث شاشة مراجعة الأسئلة لعرض حالة مزود الترجمة.

## المسار الحالي

```text
رفع PDF نصي
→ استخراج النص
→ تقسيم النص إلى بطاقات أسئلة
→ توليد قاموس مصطلحات أولي
→ ترجمة أولية عبر طبقة مزود آمنة
→ مراجعة وتعديل وحذف وترتيب
→ تصدير DOCX/PDF بتنسيق RTL
→ إدراج شعار المدرسة اختياريًا في التصدير
```

## إعدادات مزود الترجمة

الوضع الافتراضي لا يحتاج أي مفتاح:

```bash
MADARIK_AI_PROVIDER=mock
```

للتجارب المستقبلية فقط، يمكن ضبط مزود خارجي من الخادم:

```bash
MADARIK_AI_PROVIDER=openai
MADARIK_AI_API_KEY=...
MADARIK_AI_MODEL=...
```

لا تُرسل مفاتيح API إلى المتصفح ولا تظهر في endpoint الحالة.

## ما لا يدخل في هذه المرحلة

- لا OCR.
- لا نموذج إجابة.
- لا حفظ دائم للمشاريع.
- لا حسابات مستخدمين.
- لا ترجمة نصوص داخل الصور.
- لا إدراج صور الأسئلة والجداول في التصدير بعد.

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
