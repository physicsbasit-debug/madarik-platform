# API Spec - منصة مدارك Phase 1-C

Base path:

```text
/api
```

## Health

```http
GET /api/health
```

يرجع حالة الخدمة.

## Projects

### إنشاء مشروع

```http
POST /api/projects
```

Body اختياري من نوع `ProjectMetadata` بصيغة snake_case.

### قراءة مشروع

```http
GET /api/projects/{project_id}
```

### تحديث بيانات الورقة

```http
PATCH /api/projects/{project_id}/metadata
```

### تحديث الخطوة الحالية

```http
PATCH /api/projects/{project_id}/step
```

Body:

```json
{"current_step":"setup"}
```

### حفظ معلومات ملف شكلية

```http
PUT /api/projects/{project_id}/upload-info
```

Body:

```json
{"name":"sample.pdf","size":2048,"type":"application/pdf"}
```

يُستخدم هذا المسار عند إزالة الملف أو حفظ معلومات شكلية. المسار الحقيقي لرفع PDF في Phase 1-C هو المسار التالي.

### رفع PDF واستخراج النص

```http
POST /api/projects/{project_id}/upload-pdf
```

نوع الطلب:

```text
multipart/form-data
```

الحقل:

```text
file
```

يرجع جلسة المشروع مع:

```json
{
  "uploaded_file": {
    "name": "sample.pdf",
    "size": 12345,
    "type": "application/pdf"
  },
  "extracted_text": {
    "text": "...",
    "preview": "...",
    "page_count": 1,
    "character_count": 120,
    "is_text_based": true,
    "message": "تم استخراج النص من PDF نصي بنجاح."
  }
}
```

إذا كان PDF بلا نص قابل للاستخراج، يرجع `is_text_based=false` ورسالة توضّح أن الملف يحتاج OCR في مرحلة لاحقة.

### تحميل بيانات تجريبية

```http
POST /api/projects/{project_id}/demo-content
```

يرجع أسئلة وقاموسًا تجريبيين من Backend.

### تحديث سؤال

```http
PATCH /api/projects/{project_id}/questions/{question_id}
```

Body جزئي:

```json
{"translated_text":"ترجمة معدلة","marks":2,"status":"needs_review"}
```

### إعادة ترتيب الأسئلة

```http
POST /api/projects/{project_id}/questions/reorder
```

Body:

```json
{"ordered_question_ids":["q-1","q-2","q-3","q-4"]}
```

### تحديث مصطلح في القاموس

```http
PATCH /api/projects/{project_id}/glossary/{term_id}
```

Body جزئي:

```json
{"arabic_term":"مصطلح معدل","status":"approved"}
```

### حذف مشروع الجلسة

```http
DELETE /api/projects/{project_id}
```

يحذف المشروع المؤقت من الذاكرة.
