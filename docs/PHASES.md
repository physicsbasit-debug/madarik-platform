# مراحل منصة مدارك

## مراحل مغلقة

- Phase 0: Skeleton ✅
- Phase 1-A: Static Multi-Step UI ✅
- Phase 1-B: Backend API Integration ✅
- Phase 1-C: PDF Text Extraction ✅
- Phase 1-D: Question Parser ✅
- Phase 1-E1: Glossary Engine ✅
- Phase 1-E2: Translation Engine ✅
- Phase 1-F1: DOCX Export RTL ✅
- Phase 1-F2: PDF Export RTL ✅
- Phase 1-F3: Export Branding ✅

## Phase 1-G1: AI Provider Layer

### الهدف
إضافة طبقة مزود ترجمة قابلة للتبديل دون كسر المسار الحالي.

### الداخل في المرحلة
- إعدادات بيئية اختيارية: `MADARIK_AI_PROVIDER`, `MADARIK_AI_API_KEY`, `MADARIK_AI_MODEL`, `MADARIK_AI_BASE_URL`.
- بقاء `mock` هو الوضع الافتراضي الآمن.
- endpoint آمن لعرض حالة المزود دون كشف الأسرار.
- prompt ترجمة تربوي محافظ يحترم قاموس الورقة وأوامر السؤال.
- fallback تلقائي إذا لم يوجد مفتاح أو فشل المزود الخارجي.

### غير داخل المرحلة
- لا إجبار على مفتاح API.
- لا حفظ دائم.
- لا OCR.
- لا نموذج إجابة.

## المرحلة المقترحة لاحقًا

Phase 1-H: إدراج صور/جداول الأسئلة في المراجعة والتصدير أو Phase 2-A: تفعيل OCR، حسب أولوية الاختبار العملي.

---

## Phase 1-H1: Question Assets

الحالة: جاهزة للاختبار.

### الهدف

إتاحة ربط صور أو جداول يدوية ببطاقات الأسئلة، ثم تضمينها في تصدير DOCX/PDF.

### ما تم

- Endpoint لرفع مرفق سؤال.
- Endpoint لحذف مرفق سؤال.
- معاينة المرفقات في شاشة المراجعة.
- إدراج المرفقات في DOCX وPDF.
- اختبارات Backend إضافية.

### المؤجل

- استخراج الصور والجداول تلقائيًا من PDF.
- OCR.
- ترجمة النص داخل الصورة.


---

## Phase 1-I2: PDF OCR Fallback

- أضيف دعم رفع الصور PNG/JPG/WEBP لاستخراج النص الإنجليزي مبدئيًا عبر Tesseract OCR.
- بقي PDF النصي مدعومًا كما في Phase 1-C.
- لا يشمل هذا الاستخراج OCR كاملًا لملفات PDF المصوّرة متعددة الصفحات.
- endpoint الجديد: `POST /api/projects/{project_id}/upload-image-ocr`.
- النص المستخرج من الصورة يستخدم في مسار تقسيم الأسئلة الحالي.


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
