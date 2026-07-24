# Madarik Simplified User Journey — Batch 4

## النطاق

تبسيط بداية العمل وغلاف المنصة:

1. بطاقة معالجة الورقة تفتح مسار الرفع مباشرة بنقرة واحدة.
2. إلغاء نافذة اختيار المصدر التي كانت تضيف خطوة قبل الرفع.
3. إبقاء Google Drive وOneDrive كرابط ثانوي واضح لا يعطل الرحلة الأساسية.
4. إخفاء شريط سياق المشروع من الصفحة الرئيسية.
5. إخفاء تكرار حالة الحفظ في أسفل الصفحة، مع بقائها في رأس المنصة.

## الملفات المعدلة

- `frontend/src/components/PlatformShell.tsx`
- `frontend/src/features/workflow/ScienceTaskHome.tsx`
- `frontend/src/styles/simplified-platform.css`
- `backend/tests/test_simplified_user_journey_batch_4.py`

## ما لم يتغير

- عقود Backend وAPI.
- مسار المعالجة التلقائية في Batch 3.
- Google Drive وOneDrive وخدماتهما.
- المراجعة والتصدير وبنك الأسئلة.
- الفرع المعتمد `feat/madarik-science-platform-v2`.
