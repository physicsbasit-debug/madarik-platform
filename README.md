# منصة مدارك - Phase 2-A1 Persistence Foundation

منصة مدارك هي منصة تعليمية ذكية لمعالجة أوراق الاختبارات الأجنبية وتحويلها إلى موارد عربية وثنائية اللغة قابلة للمراجعة والطباعة.

## حالة هذه الحزمة

```text
Phase 1-I2: PDF OCR Fallback
الحالة: جاهزة للرفع والاختبار عبر GitHub Actions
```

## ما تضيفه Phase 1-I2

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


## Phase 1-I2 Fix 1

- تحسين استقرار OCR على GitHub Actions عبر تجهيز الصورة قبل Tesseract.
- عدم تحويل الصورة الصالحة ذات النص غير المقروء إلى فشل صلب؛ يتم حفظ رسالة واضحة للمستخدم بدلًا من ذلك.
- تثبيت حزمة خطوط DejaVu في CI لدعم اختبار OCR بصورة مستقرة.


## Phase 1-J1: Export Readiness Guard

أضيف فحص جاهزية قبل التصدير عبر endpoint:

`GET /api/projects/{project_id}/readiness`

يفحص وجود أسئلة قابلة للتصدير، وجود ترجمة، حالات تحتاج مراجعة، الدرجات، والأسئلة المحذوفة. يمنع التصدير عند وجود موانع واضحة مثل عدم وجود أسئلة أو حذف كل الأسئلة.


## Phase 1-K1: Workflow Regression Tests

أضيفت اختبارات شاملة لحماية دورة العمل الرئيسية:

PDF نصي → استخراج النص → تقسيم الأسئلة → توليد القاموس → الترجمة الأولية → فحص الجاهزية → تصدير DOCX/PDF.

الهدف من هذه المرحلة ليس إضافة ميزة جديدة، بل منع كسر المسار الرئيسي أثناء التطوير اللاحق.


## Phase 1-L1: Review Bulk Actions

أضيفت إجراءات جماعية في شاشة مراجعة الأسئلة لتسهيل اعتماد جميع الأسئلة النشطة، تحويلها إلى حالة تحتاج مراجعة، أو استعادة جميع الأسئلة المحذوفة إلى المراجعة.

Endpoint جديد:

`POST /api/projects/{project_id}/questions/bulk-status`

الهدف من المرحلة تقليل النقرات المتكررة قبل فحص الجاهزية والتصدير.


## Phase 1-M1: Project Snapshot Import/Export

أضيف حفظ واستيراد نسخة عمل بصيغة JSON من جهاز المستخدم دون حسابات ودون قاعدة بيانات دائمة.

Endpoints:

`GET /api/projects/{project_id}/snapshot`

`POST /api/projects/import-snapshot`

الهدف أن يستطيع المعلم حفظ مشروعه واستعادته لاحقًا حتى لو أُعيد تحميل الصفحة أو انتهت الجلسة المؤقتة.


## Phase 1-N1: Final UI & Documentation Polish

هذه مرحلة تنظيف نهائية قبل اختبار القبول:

- تحديث عناوين الواجهة التي كانت تشير إلى مراحل قديمة.
- إضافة وسم Phase 1-N1 في ملخص الحالة.
- تحسين نصوص الحفظ والاستيراد.
- إضافة وثيقة حالة Phase 1:
  - `docs/PHASE1_STATUS.md`
- إضافة قائمة اختبار قبول:
  - `docs/PHASE1_ACCEPTANCE_CHECKLIST.md`

لا تضيف هذه المرحلة منطقًا كبيرًا جديدًا، بل تجهز المشروع للانتقال إلى اختبار قبول حقيقي ونسخة RC1.


## Phase 1-N2: Acceptance Test Pack

أضيفت حزمة اختبار قبول قبل RC1:

- وثيقة بروتوكول اختبار القبول:
  - `docs/PHASE1_ACCEPTANCE_PROTOCOL.md`
- نموذج تقرير اختبار قبول:
  - `docs/PHASE1_ACCEPTANCE_REPORT_TEMPLATE.md`
- نص عينة لإنشاء PDF اختباري:
  - `docs/PHASE1_ACCEPTANCE_SAMPLE_TEXT.md`
- اختبارات Backend إضافية تغطي دورة قبول كاملة مع Snapshot round-trip.

هذه المرحلة لا تضيف ميزة للمستخدم النهائي، بل تؤمن الانتقال إلى RC1 بأقل قدر من الفوضى البشرية المعتادة.


## Phase 1-RC1: Release Candidate

تم تثبيت نسخة مرشحة أولى لاختبار قبول Phase 1.

### وثائق RC1

- `docs/RELEASE_NOTES_RC1.md`
- `docs/RC1_TEST_PLAN.md`
- `docs/RC1_SCOPE_LOCK.md`

### الحالة

هذه نسخة مرشحة للاختبار الداخلي وليست نسخة إنتاج نهائية. أي توسع كبير ينتقل إلى Phase 2 بدل حشره في RC1، لأن حشر الميزات في آخر لحظة هواية بشرية مشؤومة.


## Phase 2-A0: Roadmap & Scope Gate

هذه مرحلة تخطيط وتثبيت نطاق بعد نجاح Phase 1-RC1. لا تغيّر منطق التطبيق ولا تضيف ميزة تشغيلية جديدة.

### وثائق Phase 2-A0

- `docs/PHASE2_ROADMAP.md`
- `docs/PHASE2_SCOPE_GATE.md`
- `docs/PHASE2_BACKLOG.md`
- `docs/PHASE2_ARCHITECTURE_DECISIONS.md`
- `docs/PHASE2_RISK_REGISTER.md`

الهدف: اختيار المسار الصحيح لأول تطوير حقيقي في Phase 2 بدل القفز العشوائي إلى قاعدة بيانات أو AI أو حسابات كما لو أن المشروع سيرك متنقل.


## Phase 2-A1: Persistence Foundation

أضيف تخزين دائم للمشاريع باستخدام SQLite وطبقة Repository دون إدخال حسابات أو مكتبة مشاريع كاملة.

الوثيقة التفصيلية:

`docs/PHASE2_A1_PERSISTENCE_FOUNDATION.md`
