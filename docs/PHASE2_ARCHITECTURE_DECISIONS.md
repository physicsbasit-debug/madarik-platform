# منصة مدارك - Phase 2 Architecture Decisions

## القرار 1: التخزين قبل الحسابات

الحسابات لا تبدأ قبل وجود تخزين دائم. حساب مستخدم بلا تخزين منظم مجرد بطاقة اسم على مكتب فارغ.

## القرار 2: Repository Layer

يجب فصل API عن تفاصيل التخزين عبر طبقة Repository.

المسار المتوقع:

```text
API Router
→ Service
→ Repository
→ SQLite/PostgreSQL لاحقًا
```

## القرار 3: Snapshot يبقى

حتى بعد إدخال التخزين الدائم، يبقى Snapshot JSON كمسار:
- نسخ احتياطي.
- نقل مشروع.
- اختبار.
- استعادة يدوية.

## القرار 4: SQLite كبداية

SQLite مناسب لـ Phase 2-A لأنه:
- يعمل في CI.
- لا يحتاج خادمًا.
- يكفي لاختبار نموذج البيانات.
- يمكن استبداله لاحقًا بـ PostgreSQL إذا احتجنا.

## القرار 5: عدم إدخال AI حقيقي الآن

AI الخارجي مؤجل إلى C1 بعد التخزين والمكتبة. السبب أن نتائج AI تحتاج حفظًا، وسجلًا، ومراجعة، لا مجرد زر يرسل نصًا إلى الكون وينتظر فاتورة.

## القرار 6: المرفقات

في A1 يمكن حفظ المرفقات مبدئيًا داخل JSON/base64 كما هي في النموذج الحالي، لكن يجب توثيق أن التخزين الملفي أو object storage خيار لاحق إذا كبرت الأحجام.

## القرار 7: لا كسر لمسار Phase 1

كل تطوير في Phase 2 يجب أن يحافظ على:
- رفع PDF نصي.
- OCR صورة/PDF مبدئي.
- تقسيم الأسئلة.
- قاموس.
- ترجمة fallback.
- مراجعة.
- جاهزية.
- تصدير DOCX/PDF.
- Snapshot JSON.


## Phase 2-A1: Persistence Foundation

أضيف تخزين دائم للمشاريع باستخدام SQLite وطبقة Repository دون إدخال حسابات أو مكتبة مشاريع كاملة.

الوثيقة التفصيلية:

`docs/PHASE2_A1_PERSISTENCE_FOUNDATION.md`


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


## Phase 2-C1: AI Provider Hardening

تم تقوية طبقة مزود الذكاء الاصطناعي:
- حالة مزود أكثر تفصيلًا.
- إعدادات حدود ومدى الاتصال الخارجي.
- دعم `openai-compatible`.
- fallback آمن عند فشل الشبكة أو عدم الجاهزية.
- عدم كشف المفاتيح.

الوثيقة التفصيلية:

`docs/PHASE2_C1_AI_PROVIDER_HARDENING.md`


## Phase 2-RC1: Release Candidate

تم قفل نطاق Phase 2 كنسخة مرشحة:
- Release notes.
- Test plan.
- Scope lock.
- Acceptance checklist.
- لا توجد ميزة تشغيلية جديدة في هذه المرحلة.

الوثائق:
- `docs/PHASE2_RC1_RELEASE_NOTES.md`
- `docs/PHASE2_RC1_TEST_PLAN.md`
- `docs/PHASE2_RC1_SCOPE_LOCK.md`
- `docs/PHASE2_RC1_ACCEPTANCE_CHECKLIST.md`
