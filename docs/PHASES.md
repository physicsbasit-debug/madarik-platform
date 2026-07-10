# مراحل منصة مدارك

## مكتمل

- Phase 0: Project Skeleton
- Phase 1-A: Static Multi-Step UI
- Phase 1-B: Backend API Integration
- Phase 1-C: PDF Text Extraction
- Phase 1-D: Question Parser
- Phase 1-E1: Glossary Engine
- Phase 1-E2: Translation Engine
- Phase 1-F1: DOCX Export RTL

## المرحلة الحالية

### Phase 1-F3: Export Branding

الهدف: إضافة تصدير PDF فعلي أولي بتنسيق RTL للنسختين العربية والثنائية.

يدخل في المرحلة:

- خدمة `build_project_pdf_bytes` في Backend.
- Endpoint `POST /api/projects/{project_id}/export/pdf`.
- زر تحميل PDF في واجهة التصدير.
- اختبار Backend لتوليد PDF.
- استمرار تصدير DOCX دون كسر.

لا يدخل في المرحلة:

- OCR.
- شعار المدرسة.
- الصور والجداول داخل التصدير.
- AI خارجي.
- نموذج إجابة.

## قادم لاحقًا

- Phase 1-F3: تحسين التصدير بإضافة الشعار والصور/الجداول إن أمكن.
- Phase 1-G: AI Provider Layer.
- Phase 2: نسخة تدريبية مشروحة.


## Phase 1-F3: Export Branding

- رفع شعار مدرسة اختياري بصيغة PNG/JPG.
- حفظ الشعار مؤقتًا داخل ProjectSession.
- حذف الشعار من الجلسة.
- إدراج الشعار في DOCX وPDF عند التصدير.
- لا يشمل ذلك إدراج صور الأسئلة أو حفظ الشعار دائمًا.
