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

تمت مراجعة نصوص الواجهة والتوثيق وإضافة وثائق حالة Phase 1 وقائمة اختبار القبول، تمهيدًا لنسخة RC1.


## Phase 1-N2: Acceptance Test Pack

تمت إضافة وثائق اختبار القبول ونموذج تقرير قبول واختبارات Backend إضافية لحماية دورة العمل الكاملة قبل تثبيت RC1.


## Phase 1-RC1: Release Candidate

تم تثبيت نسخة مرشحة أولى بعد اكتمال مسار Phase 1 الأساسي واختبارات القبول الآلية. أي إضافات كبيرة تؤجل إلى Phase 2.


## Phase 2-A1: Persistence Foundation

أضيف تخزين دائم للمشاريع باستخدام SQLite وطبقة Repository دون إدخال حسابات أو مكتبة مشاريع كاملة.

الوثيقة التفصيلية:

`docs/PHASE2_A1_PERSISTENCE_FOUNDATION.md`


## Phase 2-A2: Project Library

أضيفت واجهة مكتبة المشاريع المحفوظة فوق SQLite:
- عرض المشاريع المحفوظة.
- فتح مشروع محفوظ.
- حذف مشروع محفوظ.
- الحفاظ على Snapshot JSON كمسار نسخ واستيراد.

الوثيقة التفصيلية:

`docs/PHASE2_A2_PROJECT_LIBRARY.md`


## Phase 2-B1: Accounts & Roles Foundation

أضيفت طبقة حسابات وصلاحيات أولية:
- إنشاء حساب المالك عند أول تشغيل.
- تسجيل الدخول والخروج.
- جلسات محفوظة في SQLite.
- أدوار أولية: owner / teacher / reviewer.

الوثيقة التفصيلية:

`docs/PHASE2_B1_ACCOUNTS_ROLES_FOUNDATION.md`


## Phase 2-B2: Project Ownership & Access Rules

أضيف ربط المشاريع بالحساب الحالي وقواعد وصول أولية فوق مكتبة المشاريع.

الوثيقة التفصيلية:

`docs/PHASE2_B2_PROJECT_OWNERSHIP_ACCESS.md`


## Phase 2-B3: User Management Lite

أضيفت إدارة حسابات خفيفة للمالك:
- عرض الحسابات.
- إنشاء حساب.
- تفعيل/تعطيل حساب.
- حماية إدارة الحسابات لتكون للمالك فقط.

الوثيقة التفصيلية:

`docs/PHASE2_B3_USER_MANAGEMENT_LITE.md`
