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
