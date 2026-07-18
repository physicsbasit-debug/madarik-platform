# Phase 4-A6d Fix 6: Marks Policy & Student Export Closure

## Scope

- Add an explicit paper-level marks policy when declared marks differ from the sum of questions.
- Allow either adopting the question total or recording a declared scaled total without altering question marks.
- Keep unresolved mismatches in `needs_review`.
- Remove the internal `مرفقات السؤال` heading from student-facing DOCX/PDF exports.
- Bound DOCX images by both width and height while preserving aspect ratio.
- Prevent unaccepted or fallback Arabic from being labeled `عربية نظيفة`.
- Preserve the translation acceptance report when only the marks policy changes.

## Marks policies

- `unresolved`: keep the mismatch warning and final review requirement.
- `use_question_total`: show the calculated question total as the paper mark.
- `scale_to_declared`: show the declared final mark and record that it is converted from the raw question total.

No question or part marks are rescaled automatically.

## Acceptance

- Unresolved `20 / 80` mismatch remains reviewable.
- `use_question_total` exports `80` as the paper mark.
- `scale_to_declared` exports `20 (محولة من 80)` and labels `80` as the raw total.
- Fallback translation exports are labeled `مسودة ترجمة تحتاج مراجعة`.
- Student exports contain diagrams without the internal attachment heading.
- Portrait and landscape images remain bounded and undistorted in DOCX.
