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

## Export

```text
POST /api/projects/{project_id}/export/docx
POST /api/projects/{project_id}/export/pdf
```

### DOCX

يرجع ملف Word بصيغة:

```text
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

### PDF

يرجع ملف PDF بصيغة:

```text
application/pdf
```

يرفض التصدير إذا لم توجد أسئلة نشطة غير محذوفة.


## School logo endpoints - Phase 1-F3

```text
POST /api/projects/{project_id}/school-logo
DELETE /api/projects/{project_id}/school-logo
```

يدعم رفع شعار PNG/JPG مؤقتًا داخل جلسة المشروع، ثم حذفه عند الحاجة. يظهر الشعار في DOCX وPDF عند التصدير.
