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
