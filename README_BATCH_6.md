# Madarik Simplified User Journey — Batch 6

## الهدف
تحويل مسار معالجة الورقة من صفحة تتراكم فيها مراحل الرفع والمعالجة والنتيجة إلى شاشة تعرض حالة واحدة فقط في كل لحظة.

## السلوك الجديد
- قبل اختيار الملف: تظهر شاشة الرفع فقط.
- أثناء القراءة والترجمة والفحص: تظهر شاشة التجهيز فقط.
- عند الخطأ: تظهر شاشة استرداد واضحة مع إعادة المحاولة.
- بعد النجاح: تظهر شاشة القرار فقط، إما مراجعة الملاحظات أو التصدير.
- يبقى تغيير الملف متاحًا من شريط صغير دون إعادة عرض مرحلة الرفع كاملة.
- شريط تقدم من ثلاث خطوات يوضح الموقع الحالي دون إضافة صفحات أو نقرات.

## الملفات
- `frontend/src/features/workflow/QuickTranslationWorkspace.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_batch_2.py`
- `backend/tests/test_simplified_user_journey_batch_3.py`
- `backend/tests/test_simplified_user_journey_batch_4.py`
- `backend/tests/test_simplified_user_journey_batch_6.py`

## سبب تحديث اختبارات Batch 2–4
كانت بعض الاختبارات السابقة مرتبطة ببنية JSX ونصوص واجهة أزيلت عمدًا في Batch 6. جرى تحديثها لتتحقق من السلوك نفسه وفق البنية الجديدة، بدل إجبار الواجهة على الاحتفاظ بعلامات قديمة غير مرئية.

## غير المتغير
لا تعديل على Backend أو API أو قاعدة البيانات أو منطق الاستخراج والترجمة والمراجعة والتصدير.
