# API Spec - منصة مدارك Phase 1-E1

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

### رفع PDF واستخراج النص

```http
POST /api/projects/{project_id}/upload-pdf
```

نوع الطلب: `multipart/form-data`

الحقل: `file`

يرجع جلسة المشروع مع معلومات الملف ونتيجة استخراج النص. إذا كان PDF بلا نص قابل للاستخراج، يرجع `is_text_based=false` ورسالة توضّح أن الملف يحتاج OCR في مرحلة لاحقة.

### تقسيم النص المستخرج إلى أسئلة

```http
POST /api/projects/{project_id}/parse-questions
```

يتطلب وجود `extracted_text` ناتج من PDF نصي. يحول النص إلى بطاقات `QuestionItem` باستخدام قواعد أولية، ويضع الأسئلة الناتجة بحالة `needs_review`.

### توليد قاموس الورقة من الأسئلة

```http
POST /api/projects/{project_id}/glossary/generate
```

يتطلب وجود بطاقات أسئلة. يستخدم محرك Phase 1-E1 القائم على قائمة مصطلحات علمية أولية لاستخراج مصطلحات للمعلم فقط. المصطلحات الناتجة تكون `source=detected` و`status=needs_review`.

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
