# Phase 4-A6b: Full Exam Translation and Review Acceptance

## Goal

Extend the full-paper intake completed in Phase 4-A6a into a deterministic,
persisted acceptance layer for translation and teacher review.

The phase does not replace the Phase 4-A5 batch translator. It consumes the
existing isolated batch outcomes, validates the current translated content,
and reports whether the complete paper is:

- accepted,
- complete but still needs teacher review,
- incomplete, or
- contains questions whose translation failed safely.

## Backend scope

### FullExamTranslationReport

The project snapshot now persists a full-paper translation report containing:

- total, active, deleted, translated, accepted, review, incomplete, and failed
  question counts,
- completion percentage,
- translated item counts for whole questions and structured parts,
- urgent-review and safe-failure counts,
- glossary compliance violations,
- scientific-fidelity violations,
- source-page and linked-layout preservation,
- a question-by-question acceptance summary,
- deterministic checks and warnings.

The report is backward compatible because old snapshots receive `null` for the
new optional field.

### Report lifecycle

The report is rebuilt when:

- questions are parsed,
- the glossary changes,
- layout-page links change,
- a full translation batch completes,
- one question is retried,
- a question is edited,
- question review statuses change,
- questions are reordered.

Upstream file or metadata changes clear stale translation acceptance.

### Single-question retry

A new endpoint retries one active question without retranslating the rest of
the paper:

```text
POST /api/projects/{project_id}/questions/{question_id}/retry-translation
```

The endpoint:

1. rejects deleted questions,
2. translates only the selected question and its structured parts,
3. preserves all other question content and source links,
4. replaces the selected question's previous batch outcomes,
5. rebuilds batch counts and the full-paper acceptance report.

## Acceptance rules

A question is classified as:

- `accepted`: translated, scientifically compliant, and approved by the teacher,
- `needs_review`: translated but not approved or containing deterministic
  glossary/fidelity violations,
- `untranslated`: one or more required text items have no translation,
- `failed`: the latest automated batch retained a safe failure that is not yet
  resolved by teacher approval,
- `deleted`: excluded from acceptance totals.

The paper status is:

- `accepted` when every active question is accepted,
- `needs_review` when translation is complete but review or compliance work
  remains,
- `incomplete` when active questions are missing translations,
- `failed` when unresolved safe failures remain.

## Frontend scope

The review workspace now shows:

- paper translation completion percentage,
- accepted, review, incomplete, and failed question counts,
- glossary and scientific-fidelity violation counts,
- a per-question translation acceptance message,
- an isolated `إعادة ترجمة السؤال` action for any non-accepted active question.

## Compatibility

- The existing `/translate-questions` endpoint remains unchanged for callers.
- The Phase 4-A5 batch summary remains available.
- Manual question edits clear stale provider batch details but immediately
  rebuild acceptance from the current saved content.
- Existing project snapshots remain importable.

## Verification targets

After applying this phase to the Phase 4-A6a baseline:

```text
Backend full suite: 208 passed
Frontend lint: passed
Frontend production build: passed
```

The focused acceptance file adds five tests covering:

1. incomplete untranslated papers,
2. complete translation before and after teacher approval,
3. glossary and scientific-fidelity violations,
4. failed-question retry and batch-outcome replacement,
5. API translation, isolated retry, and final full-paper acceptance.
