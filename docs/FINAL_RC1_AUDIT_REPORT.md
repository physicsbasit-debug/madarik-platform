# Final RC-1: Release Audit Baseline

## القرار

الحالة الحالية: **FIX REQUIRED قبل اعتماد المرشح النهائي**.

لا توجد ميزة جديدة ضمن هذه المرحلة. نطاقها تنظيف المستودع، تقوية بوابة CI، وتوثيق شروط الإغلاق.

## النتائج المؤكدة

### PASS

- الفرع النهائي مبني على `main` بعد دمج Phase 4-B1.
- README يعكس `2.0.0-rc.1` وPhase 4-B1.
- اختبارات Phase 4-B1 المركزة نجحت سابقًا: `58 passed`.
- اختبارات Backend الكاملة نجحت سابقًا: `245 passed`.
- Frontend lint وproduction build نجحا سابقًا.
- ملف `backend/.env.example` يستخدم قيمًا بديلة ولا يحتوي اسم نموذج افتراضي وهمي.
- قواعد تجاهل ملفات البيئة وقواعد البيانات موجودة.

### FIX REQUIRED

1. توجد ملفات Python bytecode متتبعة داخل:
   - `backend/app/__pycache__/`
2. Workflow الحالي لا يشغّل Frontend lint.
3. Workflow الحالي يحذف `package-lock.json` ويستخدم تثبيتًا غير حتمي بدل `npm ci`.
4. اسم Workflow واسم ملفه ما زالا مرتبطين بمراحل قديمة بدل بوابة الإصدار.

### POLISH

- توجد Issues قديمة مفتوحة للمراحل 1-A و1-B و1-C رغم تنفيذها.
- توجد وثائق قبول تاريخية مثل Phase 2-RC1. تبقى كسجل تاريخي ولا تُستخدم بوصفها بوابة الإصدار الحالية.
- توجد سكربتات Fix قديمة في جذر المستودع. لا تُحذف في هذه الدفعة ما لم يثبت أنها غير مطلوبة.

### LIVE BLOCKER

لا يُعلن الإصدار إنتاجيًا قبل:

- إعداد مزود خارجي حقيقي وموديل صالح.
- ترجمة ورقة Cambridge كاملة.
- إثبات أن الترجمة من المزود الخارجي وليست `fallback`.
- نجاح حراس العربية والقاموس والرموز العلمية.
- مراجعة Word وPDF بصريًا.

## ملفات Final RC-1

- `.github/workflows/phase0-check.yml`
- `.gitignore`
- `RUN_FINAL_RC_CLEANUP.py`
- `RUN_FINAL_RC_TESTS.sh`
- `CHANGELOG.md`
- `docs/FINAL_RELEASE_CANDIDATE_CHECKLIST.md`
- `docs/FINAL_RELEASE_ACCEPTANCE.md`

## معيار الإغلاق

تُغلق Final RC-1 تقنيًا بعد:

- تشغيل سكربت التنظيف.
- نجاح بوابة Final RC محليًا.
- نجاح GitHub Actions.
- بقاء الاختبار الحي مسجلًا بوضوح بوصفه مانع الإصدار الإنتاجي.
