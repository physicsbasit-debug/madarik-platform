# مراحل منصة مدارك

## نقاط الاستقرار المنجزة

- Phase 0: Project Skeleton ✅
- Phase 1-A: Static Multi-Step UI ✅
- Phase 1-B: Backend API Integration ✅
- Phase 1-C: PDF Text Extraction ✅
- Phase 1-D: Question Parser ✅
- Phase 1-E1: Glossary Engine ✅
- Phase 1-E2: Translation Engine ✅
- Phase 1-F1: DOCX Export RTL ✅

## Phase 1-F1: DOCX Export RTL

### الهدف

إضافة تصدير Word حقيقي بصيغة DOCX للنسخة العربية أو الثنائية، مع دعم RTL ورأس ورقة رسمي.

### يدخل في المرحلة

- خدمة `export.py`.
- Endpoint `POST /api/projects/{project_id}/export/docx`.
- زر تحميل Word من شاشة التصدير.
- تصدير الأسئلة غير المحذوفة فقط.
- إعادة ترقيم الأسئلة في الملف النهائي.
- رأس RTL ببيانات الورقة.
- اختبارات Backend للتصدير.

### مؤجل

- PDF.
- إدراج الصور والجداول.
- شعار المدرسة.
- AI خارجي.
- OCR.
