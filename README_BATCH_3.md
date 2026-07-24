# Madarik Simplified User Journey — Batch 3

## النطاق

تحويل معالجة الورقة إلى رحلة شبه تلقائية:

1. يختار المستخدم الملف.
2. تنتظر الواجهة اكتمال قراءة الملف.
3. تبدأ عملية استخراج الأسئلة والترجمة وفحص الجاهزية تلقائيًا.
4. تظهر للمستخدم نتيجة واحدة: مراجعة الملاحظات أو التصدير.

## الملفات المعدلة

- `frontend/src/features/workflow/QuickTranslationWorkspace.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_batch_3.py`

## ما لم يتغير

- عقود Backend وAPI.
- منطق استخراج النص والأسئلة.
- الترجمة وحراس الجودة.
- المراجعة الاحترافية.
- تصدير DOCX وPDF.
- الفرع المعتمد `feat/madarik-science-platform-v2`.
