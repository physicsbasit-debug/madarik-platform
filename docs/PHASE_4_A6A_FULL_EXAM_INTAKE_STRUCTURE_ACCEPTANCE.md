# Phase 4-A6a: Full Exam Intake and Structure Acceptance

## Goal

Accept a complete text-based exam PDF as one structured paper before translation. The phase preserves page boundaries, detects the cover and semantic blank pages, identifies sequential main questions, joins continuation pages, verifies question totals against the paper total, and links PDF page snapshots to the correct questions.

## Scope

- Preserve selectable text for every PDF page.
- Classify pages as cover, question, blank, or other.
- Detect sequential main questions without treating page numbers, graph values, or paper codes as questions.
- Keep questions that continue onto later pages together.
- Detect `[Total: n]` for each main question.
- Compare the sum of question totals with the total declared on the cover.
- Store source page ranges on every parsed question.
- Auto-link full-page PDF layout snapshots using source page numbers.
- Persist a `FullExamIntakeReport` in project sessions and snapshots.
- Display the structural acceptance summary in the review workspace.

## Acceptance reference

The official acceptance sample for this phase is a 16-page Cambridge IGCSE Physics specimen paper with:

- 16 pages.
- 1 cover page.
- 1 semantic blank page.
- 12 sequential main questions.
- 80 total marks.
- 2 questions that continue onto a second page.
- Multiple figures and scientific diagrams.

Expected report status: `accepted`.

## Safety and compatibility

- Existing projects without page metadata remain valid.
- Existing flat-text question parsing remains the fallback when page metadata is unavailable.
- OCR and image intake remain supported without pretending that partial OCR is a complete-paper acceptance result.
- The phase does not change translation prompts or providers.
- Whole-page links are only structural references; question-specific diagram cropping remains a teacher review action.
## Fix 2: full layout page coverage

The layout-asset API now requests snapshots for every page in a normal full exam, up to a safety cap of 24 pages per upload. The lower-level renderer keeps its historical three-page default for direct legacy calls, so older lightweight workflows remain bounded while the complete-paper API can cover the 16-page acceptance sample.

Acceptance checks include:

- Direct renderer calls without `max_pages` still process only the first 3 pages.
- The `/layout-assets/pdf` API processes all pages when the document has 24 pages or fewer.
- The 16-page Cambridge reference therefore produces 16 page snapshots before page-aware question linking.
