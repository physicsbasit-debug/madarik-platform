# منصة مدارك - Phase 2 Backlog

## الأولوية 1: التخزين الدائم

### Phase 2-A1: Persistence Foundation

- إضافة SQLite.
- إنشاء جداول للمشاريع.
- حفظ metadata.
- حفظ extracted_text.
- حفظ questions.
- حفظ glossary.
- حفظ logo/assets بصيغة آمنة أو base64 مؤقتًا.
- إضافة Repository layer.

### Phase 2-A2: Project Library

- عرض قائمة المشاريع.
- فتح مشروع.
- حذف مشروع.
- تكرار مشروع.
- بحث بسيط.

## الأولوية 2: المستخدمون والصلاحيات

### Phase 2-B1: Accounts & Roles

- نموذج مستخدم.
- Login بسيط.
- ربط المشاريع بالمستخدم.
- صلاحيات أولية.

## الأولوية 3: الترجمة الذكية

### Phase 2-C1: AI Provider Hardening

- إعداد OpenAI-compatible provider.
- إعداد Gemini-compatible provider لاحقًا.
- سجل حالة الترجمة.
- حماية من فشل الشبكة.
- منع كشف المفاتيح.

## الأولوية 4: الملفات المعقدة

### Phase 2-D1: PDF Layout & Assets

- استخراج صور من PDF.
- ربط الصور بالأسئلة يدويًا/شبه تلقائي.
- تحسين OCR متعدد الصفحات.

## الأولوية 5: القيمة التربوية

### Phase 2-E1: Answer Key Draft

- مسودة نموذج إجابة.
- مستويات ثقة.
- تمييز أنها للمعلم فقط.

### Phase 2-F1: Educational Analysis

- تصنيف أفعال السؤال.
- تحليل توزيع الدرجات.
- ملاحظات جودة الورقة.
- توصيات مراجعة.

## المؤجل عمدًا

- نظام مدرسة متعدد المستخدمين كامل.
- دفع إلكتروني.
- مكتبة أوراق عامة.
- مشاركة عامة للأوراق.
- OCR عربي إنتاجي.


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


## Phase 2-D1: PDF Layout & Assets Extraction

أضيف استخراج مبدئي للقطات تخطيط PDF:
- حفظ `layout_assets` داخل المشروع.
- endpoint لاستخراج لقطات تخطيط من PDF.
- عرض اللقطات في خطوة الاستخراج.
- حذف اللقطات من الواجهة.

الوثيقة التفصيلية:

`docs/PHASE2_D1_PDF_LAYOUT_ASSETS.md`
