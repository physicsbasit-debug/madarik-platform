# Phase 10-B: Final Release Candidate Consolidation and Sign-off

## الإصدار

`2.0.0-rc.2`

## الهدف

توحيد جميع مكونات المرشح النهائي وإغلاق بوابة الإصدار التقنية في مسار واحد
قابل لإعادة التنفيذ، دون إضافة وظائف تعليمية جديدة أو تخفيف حراس القبول.

## ما تم تثبيته

- توحيد الإصدار بين Backend وFrontend وpackage-lock وREADME وملف الحالة.
- ترقية بيانات الإصدار الداخلية إلى `Phase 10-B`.
- إضافة `RUN_PHASE10_B_RC_PREFLIGHT.py`.
- توحيد GitHub Actions تحت `Phase 10-B Final RC Gate`.
- حفظ تقرير Preflight كأثر من GitHub Actions لمدة 14 يومًا.
- إضافة حالة إصدار مقروءة آليًا في `docs/FINAL_RELEASE_STATUS.json`.
- إبقاء الاختبار الحي والمراجعة البصرية كحاجزين مفتوحين.

## بوابة RC الآلية

تتحقق البوابة من:

1. نظافة الملفات المتتبعة وعدم وجود SQLite أو ZIP أو Patch أو bytecode.
2. عدم وجود ملفات أسرار أو مفاتيح ظاهرة أو عنوان سجل npm داخلي.
3. تطابق الإصدار والقناة والمرحلة والعنوان.
4. وجود Workflow إصدار واحد فقط وعدم استخدام اسم بوابة قديم.
5. سلامة OpenAPI وعدم تكرار `operationId`.
6. نجاح `/api/health/readiness` دون كشف أسرار أو مسارات تشغيل.
7. نجاح الاختبارات المركزة والكاملة.
8. نجاح `npm ci` وESLint وVite production build.
9. سلامة المسافات النهائية في Git.

## سياسة الإصدار

نجاح Phase 10-B يعني أن النسخة مرشح تقني نهائي، ولا يعني أنها إنتاجية.
تبقى الإجراءات التالية إلزامية قبل Tag أو GitHub Release:

- ترجمة ورقة Cambridge كاملة بمزود خارجي حقيقي.
- التحقق من عدم اعتماد fallback.
- مراجعة DOCX وPDF بصريًا.
- تعبئة محضر القبول النهائي بالأدلة.
- إغلاق جميع `LIVE BLOCKER` و`FIX REQUIRED`.

## معيار القبول

- `RUN_PHASE10_B_RC_PREFLIGHT.py`: PASS.
- اختبارات Backend: PASS.
- Frontend lint/build: PASS.
- GitHub Actions: GREEN.
- حالة الإنتاج: `blocked` حتى القبول الحي والبصري.
- الإصدار: `2.0.0-rc.2`.
- المرحلة: `Phase 10-B`.
