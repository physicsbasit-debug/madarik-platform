# API Spec - منصة مدارك

## Health

```text
GET /api/health
```

## Projects

```text
POST /api/projects
GET /api/projects/{project_id}
PATCH /api/projects/{project_id}/metadata
PATCH /api/projects/{project_id}/step
DELETE /api/projects/{project_id}
```

## Translation provider status - Phase 1-G1

```text
GET /api/projects/translation-provider/status
```

يعرض حالة مزود الترجمة دون كشف مفاتيح API.

Response fields:

```text
provider
configured
model
fallback
```

## Upload / extraction

```text
POST /api/projects/{project_id}/upload-pdf
POST /api/projects/{project_id}/parse-questions
```

## Glossary / translation

```text
POST  /api/projects/{project_id}/glossary/generate
PATCH /api/projects/{project_id}/glossary/{term_id}
POST  /api/projects/{project_id}/translate-questions
```

## Questions

```text
PATCH /api/projects/{project_id}/questions/{question_id}
POST  /api/projects/{project_id}/questions/reorder
```

## School logo endpoints - Phase 1-F3

```text
POST   /api/projects/{project_id}/school-logo
DELETE /api/projects/{project_id}/school-logo
```

يدعم رفع شعار PNG/JPG مؤقتًا داخل جلسة المشروع، ثم حذفه عند الحاجة. يظهر الشعار في DOCX وPDF عند التصدير.

## Export

```text
POST /api/projects/{project_id}/export/docx
POST /api/projects/{project_id}/export/pdf
```

يرفض التصدير إذا لم توجد أسئلة نشطة غير محذوفة.

---

## Phase 1-H1: Question assets

### رفع مرفق سؤال

```text
POST /api/projects/{project_id}/questions/{question_id}/assets
```

يرفع صورة أو جدولًا بصيغة PNG/JPG ويربطه ببطاقة سؤال محددة داخل جلسة المشروع المؤقتة.

القيود المؤقتة:

- PNG أو JPG/JPEG فقط.
- حد الحجم: 2MB.
- لا يتم استخراج المرفقات تلقائيًا من PDF في هذه المرحلة.

### حذف مرفق سؤال

```text
DELETE /api/projects/{project_id}/questions/{question_id}/assets/{asset_id}
```

يحذف مرفقًا محددًا من بطاقة السؤال داخل جلسة المشروع المؤقتة.


---

## Phase 1-I1: Image OCR Intake

- أضيف دعم رفع الصور PNG/JPG/WEBP لاستخراج النص الإنجليزي مبدئيًا عبر Tesseract OCR.
- بقي PDF النصي مدعومًا كما في Phase 1-C.
- لا يشمل هذا الاستخراج OCR كاملًا لملفات PDF المصوّرة متعددة الصفحات.
- endpoint الجديد: `POST /api/projects/{project_id}/upload-image-ocr`.
- النص المستخرج من الصورة يستخدم في مسار تقسيم الأسئلة الحالي.
