# API_SPEC - منصة مدارك

## Health

`GET /api/health`

## Projects

### إنشاء مشروع

`POST /api/projects`

### قراءة مشروع

`GET /api/projects/{project_id}`

### تحديث بيانات الورقة

`PATCH /api/projects/{project_id}/metadata`

### تحديث الخطوة الحالية

`PATCH /api/projects/{project_id}/step`

### رفع PDF واستخراج النص

`POST /api/projects/{project_id}/upload-pdf`

### تقسيم النص إلى أسئلة

`POST /api/projects/{project_id}/parse-questions`

### توليد قاموس الورقة

`POST /api/projects/{project_id}/glossary/generate`

### ترجمة الأسئلة

`POST /api/projects/{project_id}/translate-questions`

### تحديث سؤال

`PATCH /api/projects/{project_id}/questions/{question_id}`

### إعادة ترتيب الأسئلة

`POST /api/projects/{project_id}/questions/reorder`

### تحديث مصطلح

`PATCH /api/projects/{project_id}/glossary/{term_id}`

### تصدير DOCX

`POST /api/projects/{project_id}/export/docx`

يرجع ملف Word حقيقي بصيغة DOCX.

- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- لا يصدّر الأسئلة المحذوفة.
- يعيد ترقيم الأسئلة وفق ترتيب المعلم.
- يدعم النسخة العربية والثنائية حسب `metadata.output_mode`.

### حذف المشروع المؤقت

`DELETE /api/projects/{project_id}`
