# Phase 0-A: V2 Data Contracts

## QuestionV2

```json
{
  "id": "string",
  "project_id": "string",
  "source_document_id": "string",
  "source_page": 1,
  "source_question_number": "1",
  "original_text": "string",
  "translated_text": "string",
  "parts": [],
  "marks": 0,
  "science_domain": "general_science | physics | chemistry | biology | environmental_science",
  "grade": 1,
  "unit_id": "string | null",
  "lesson_id": "string | null",
  "learning_outcome_ids": [],
  "cognitive_category": "knowledge | application | reasoning | unclassified",
  "difficulty_level": "support | basic | intermediate | advanced | unclassified",
  "question_type": "string",
  "estimated_time_minutes": 0,
  "model_answer": "string | null",
  "mark_scheme": [],
  "common_mistakes": [],
  "approval_status": "draft | needs_review | approved | rejected",
  "bank_status": "not_added | candidate | added | archived",
  "classification_confidence": 0.0,
  "duplicate_signature": "string | null",
  "diagram_ids": [],
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## CurriculumDocument

```json
{
  "id": "string",
  "cloud_source_id": "string | null",
  "grade": 1,
  "science_domain": "physics",
  "document_type": "student_book | teacher_guide | curriculum_document | learning_outcomes | assessment_guide | other",
  "title": "string",
  "curriculum_version": "string | null",
  "academic_year": "string | null",
  "language": "ar | en | bilingual",
  "approval_status": "draft | approved | archived",
  "checksum": "string | null",
  "last_synced_at": "ISO-8601 | null"
}
```

## OriginalAssessment

```json
{
  "id": "string",
  "source_document_id": "string",
  "grade": 1,
  "science_domain": "physics",
  "assessment_type": "short_quiz | unit_test | midterm | final | specimen | other",
  "academic_year": "string | null",
  "publisher": "string | null",
  "language": "en",
  "total_marks": 0,
  "question_count": 0,
  "translation_status": "not_started | processing | needs_review | approved",
  "rights_status": "unknown | internal_use | permitted | restricted"
}
```

## CloudSource

```json
{
  "id": "string",
  "provider": "google_drive | onedrive",
  "file_id": "string",
  "folder_id": "string | null",
  "file_name": "string",
  "mime_type": "string",
  "web_url": "string | null",
  "version": "string | null",
  "checksum": "string | null",
  "last_modified_at": "ISO-8601 | null",
  "last_synced_at": "ISO-8601 | null",
  "access_scope": "read_only | read_write"
}
```

## QuestionBankItem

```json
{
  "id": "string",
  "question_id": "string",
  "status": "candidate | approved | archived",
  "usage_count": 0,
  "last_used_at": "ISO-8601 | null",
  "tags": [],
  "created_by": "string",
  "approved_by": "string | null"
}
```

## AssessmentBlueprint

```json
{
  "id": "string",
  "grade": 1,
  "science_domain": "physics",
  "unit_ids": [],
  "lesson_ids": [],
  "total_marks": 0,
  "duration_minutes": 0,
  "knowledge_percentage": 0,
  "application_percentage": 0,
  "reasoning_percentage": 0,
  "difficulty_distribution": {
    "support": 0,
    "basic": 0,
    "intermediate": 0,
    "advanced": 0
  },
  "question_type_distribution": {}
}
```

## DifferentiatedActivity

```json
{
  "id": "string",
  "grade": 1,
  "science_domain": "physics",
  "learning_outcome_ids": [],
  "level": "support | basic | advanced | enrichment | remedial",
  "activity_type": "worksheet | exit_ticket | group_task | individual_task | practical | homework",
  "student_instructions": "string",
  "teacher_guidance": "string",
  "model_answer": "string | null",
  "estimated_time_minutes": 0
}
```
