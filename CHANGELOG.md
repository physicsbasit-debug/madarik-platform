# سجل تغييرات منصة مدارك

يتبع هذا السجل مبدأ توثيق التغييرات المهمة للمستخدم والمطور، دون اعتبار النسخة إنتاجية قبل اجتياز بوابة القبول الحي.

## [غير منشور]

### أضيف

- غلاف استخدام مبسط من ثلاث مراحل: البدء والرفع، المراجعة، والتصدير.
- تحديد الكل والحذف الجماعي في مكتبة المشاريع.
- اعتماد جماعي للمصطلحات المكتملة في قاموس الورقة.
- قسم أدوات متقدمة يحافظ على الاستخراج والقاموس واللقطات دون إغراق الواجهة الرئيسية.

### متبقٍ قبل الإصدار النهائي

- ترجمة ورقة Cambridge كاملة عبر مزود ذكاء اصطناعي خارجي حقيقي.
- التأكد من أن الترجمة المقبولة ليست `fallback`.
- مراجعة DOCX وPDF بصريًا.
- توثيق نتيجة القبول النهائية.
- إنشاء Tag وGitHub Release بعد اجتياز جميع البوابات.


## [2.0.0-rc.2] - 2026-07-23

### ثُبّت

- توحيد إصدار المرشح النهائي عبر Backend وFrontend وpackage-lock وREADME وملف حالة الإصدار.
- ترقية بيانات الإصدار إلى `Phase 10-B: Final Release Candidate Consolidation and Sign-off`.
- إضافة بوابة `RUN_PHASE10_B_RC_PREFLIGHT.py` لفحص المستودع والإصدار والـWorkflow وOpenAPI والجاهزية.
- توحيد GitHub Actions تحت بوابة إصدار واحدة مع حفظ تقرير Preflight كأثر.
- إضافة اختبارات إصدار مركزة لبيانات RC وحالة الحواجز وWorkflow النهائي.
- إبقاء Tag وGitHub Release محجوبين حتى القبول الحي والمراجعة البصرية.

### تحقق

- Phase 10-A وFixes 1–3 مغلقة تقنيًا.
- Frontend lint وproduction build اجتازا GitHub Actions قبل بدء Phase 10-B.
- القبول الحي لمزود خارجي ومراجعة DOCX/PDF ما زالا حاجزين إلزاميين.

## [2.0.0-rc.1] - 2026-07-19

### أضيف

- رحلة متعددة الخطوات لمعالجة أوراق الاختبارات.
- استخراج النص من PDF ودعم OCR fallback.
- مراجعة الأسئلة والأجزاء الهرمية والدرجات.
- استخراج وربط وقص الأصول البصرية.
- قاموس مصطلحات ومراجعة ترجمة.
- دعم Gemini وOpenAI Responses ومزودات OpenAI-compatible.
- حراس جودة عربية وقاموس ورموز علمية.
- منع اعتماد ترجمة `fallback`.
- تصدير DOCX وPDF مع RTL وأصول بصرية.
- حفظ المشاريع في SQLite واستيراد وتصدير Snapshot.
- حسابات وأدوار وصلاحيات أولية.
- بوابات قبول للرحلة الكاملة والترجمة والتصدير.

### صُحح

- سلامة الأسس والرموز العلمية في التصدير.
- فقد الرسوم والأصول البصرية.
- اتساق الدرجات وسياسة نسخة الطالب.
- استعادة المشروع النشط بعد تحديث الصفحة.
- حفظ وترتيب الأجزاء الرئيسية والفرعية.
- عقد `store` المختلف بين OpenAI Responses وGemini generateContent.

### تحقق

- اختبارات Phase 4-B1 المركزة: `58 passed`.
- اختبارات Backend الكاملة: `245 passed`.
- Frontend lint: ناجح.
- Frontend production build: ناجح.

### حالة الإصدار

هذه نسخة مرشحة تقنيًا، وليست إصدارًا إنتاجيًا نهائيًا حتى اجتياز الاختبار الحي لورقة Cambridge كاملة.

### Final UX RTL-1

- اعتماد نموذج مساحة عمل من ثلاث مراحل بواجهة RTL كاملة.
- إضافة شريط مراحل ثابت في يمين الشاشة.
- إضافة شريط علوي مختصر للمشروع وحالة الاتصال والإجراءات العامة.
- إضافة شريط مؤشرات للحالة دون تغيير منطق المشروع.
- نقل الحساب والصلاحيات إلى قسم قابل للفتح.
- الحفاظ على محركات البدء والمراجعة والتصدير وعقود API الحالية.

### Final UX RTL-3 Fix 1: Fast Initial Extraction

- فصل استخراج النص الأولي عن تحليل لقطات التخطيط والقص.
- إنهاء حالة الانتظار فور جاهزية النص بدل انتظار معالجة الصور.
- إضافة مراحل مرئية للرفع وقراءة PDF وOCR والنجاح والفشل.
- إضافة عداد زمن وإعادة محاولة آمنة عند فشل القراءة.
- إبقاء تحليل الرسوم داخل مرحلة المراجعة والأدوات المتقدمة.

### Final UX RTL-3 Fix 2: Pages Preview & Drag Drop

- Added real drag-and-drop file selection to the upload zone.
- Added visual feedback while a file is dragged over the upload area.
- Replaced the generic backend failure message on GitHub Pages with an explicit preview-only explanation.
- Kept extraction, OCR, translation, cropping, and export dependent on a hosted Backend.

### Final UX RTL-4: Export & Readiness Workspace

- Rebuilt the export screen around one clear readiness summary.
- Added Arabic/bilingual output selection and DOCX/PDF format selection.
- Added school identity and paper preview cards.
- Added one primary export action for selected formats.
- Moved acceptance gates, educational analysis, quality tools, and answer key into a collapsed advanced section.

### Final UX RTL-4 Fix 2: Final Visual Closure

- Moved the review translation action into the bulk action bar.
- Removed the redundant next-stage action from the final export stage.
- Strengthened output mode and file format cards.
- Combined paper preview, school identity, and readiness in one balanced row.
- Reduced final-page vertical spacing and clarified disabled navigation.

### Final UX RTL-4 Fix 3: Export Responsive Layout Repair

- Repaired output-mode and file-format cards for realistic screen widths.
- Removed fake letter-based icons and prevented word fragmentation.
- Reduced preview layout to preview plus readiness.
- Moved school identity to a full-width row.
- Stacked export status and the primary export action.
- Added medium and small screen responsive rules.

### Phase 5-A: Render Backend Preview

- Added a Dockerized FastAPI deployment with Tesseract OCR.
- Added a Render Blueprint with health checks and secret placeholders.
- Added configurable CORS origins for GitHub Pages.
- Added a GitHub Pages workflow that reads the Backend URL from a repository variable.
- Added Vite base-path support for project Pages.
- Documented the free-preview persistence limitation.

### Final UX Professional Redesign

- Redesigned start/upload, review, and export workspaces as one consistent RTL product shell.
- Added project overview and review summary panels.
- Rebalanced review columns and bulk actions.
- Separated readiness refresh from advanced reports.
- Rebuilt marks-policy choices and export preview hierarchy.
- Preserved all functional contracts.

### Final UX Stable Merge

- Extracted the approved UX redesign from `feat/final-ux-simplification`.
- Preserved `main` as the clean deployment baseline.
- Excluded Render, Docker, CORS, and experimental Pages deployment changes.
- Added focused safety checks for the merge package.

### Phase 0-A: V2 Scope, Architecture, and Data Contracts

- Locked Madarik V2 to science subjects for grades 1–12.
- Declared quick translation, curriculum library, question bank, assessment builder, differentiated activities, and science diagrams as core workflows.
- Declared Google Drive as the first cloud source and deferred OneDrive.
- Added V2 architecture, roadmap, data contracts, decisions, and UI simplification plan.
- Added a machine-readable V2 scope contract and focused tests.
- No production UI, Backend logic, persistence, or API behavior was changed.

### Phase 0-B: V2 Navigation and Task-Oriented Home

- Added a task-oriented V2 home for science teachers.
- Added real entry points for quick and professional translation.
- Added non-interactive roadmap cards for future V2 modules.
- Added a return-to-tasks control from the current workspace.
- Added responsive RTL styling and focused tests.
- No Backend, API, persistence, extraction, translation, or export logic was changed.

### Phase 1: Quick Translation Workflow

- Added a dedicated quick translation workspace.
- Added one-action orchestration for parsing, translation, and readiness checks.
- Added direct transitions to professional review and export.
- Added clear extraction, processing, and readiness states.
- Repaired the Phase 0-B ScienceTaskHome import placement in App.tsx.
- Added responsive RTL styling, documentation, and focused tests.
- No Backend API contract, persistence model, or export implementation was changed.

### Phase 2: Curriculum Structure for Grades 1–12

- Added curriculum types for grades, semesters, science subjects, units, lessons, and learning outcomes.
- Added a local science curriculum seed covering the structural range from grades 1 to 12.
- Added a repository boundary so UI components do not import seed content directly.
- Added a responsive RTL curriculum browser.
- Activated the curriculum library card on the V2 task home.
- Added documentation and focused tests.
- No Google Drive, Backend persistence, or official curriculum content was added.

### Phase 3-A: Google Drive Source Foundation

- Added read-only Google Drive source models, service, and API routes.
- Added disabled, mock, and Google API provider modes.
- Added safe status reporting without exposing access tokens.
- Added folder-scoped file listing and import foundation.
- Added a Google Drive source panel inside the curriculum browser.
- Repaired the malformed CurriculumBrowser import from Phase 2.
- Added documentation and focused tests.
- No OAuth flow, project persistence, question bank, or OneDrive integration was added.

### Phase 3-B: Curriculum Source Persistence

- Added persistent curriculum source attachments to projects.
- Added curriculum context metadata and duplicate protection.
- Added list, attach, and delete API operations.
- Added persisted source display and unlinking in the curriculum browser.
- No binary persistence, automatic parsing, source sync, or question linking was added.

### Phase 3-C: Source Version Tracking

- Added current, changed, missing, and unverifiable source states.
- Added checksum-first and modified-time fallback comparison.
- Added project-level source refresh checks.
- Added per-source status metadata and frontend badges.
- No automatic download, replacement, polling, or content reprocessing was added.

### Phase 3-D: Accept Updated Source and Preserve Version History

- Added manual acceptance of changed Google Drive source versions.
- Added metadata history for previous source versions.
- Added version history display in the curriculum source panel.
- Updated README with the current V2 status and next phase.
- No automatic replacement, content reprocessing, or version restoration was added.

### Phase 4-A: Science Question Classification Foundation

- Added knowledge, application, reasoning, and unclassified categories.
- Added classification confidence, reason, and source fields.
- Added deterministic automatic classification and manual override.
- Added classification controls to the existing question review screen.
- Reused the current question update API.
- Updated README with the current V2 status.
- No bulk classification, curriculum linking, difficulty estimation, or question bank was added.

### Phase 4-B: Curriculum Linking and Classification Review

- Added curriculum-link fields to questions and question patches.
- Added grade, domain, semester, subject, unit, lesson, and learning-outcome selection.
- Added a curriculum-link card to the existing question review screen.
- Added review summary counts for complete, unclassified, and unlinked questions.
- Repaired the malformed Phase 4-A import in ReviewStep.
- Updated README with the current V2 status.
- No AI linking, bulk linking, official curriculum import, or question-bank insertion was added.

### Phase 5-A: Question Bank Data Model and Persistence

- Added a dedicated SQLite question-bank table and repository.
- Added full question snapshots with content fingerprints.
- Added project-scoped list, save/update, and delete API routes.
- Added question-bank controls to the review screen.
- Prevented duplicate rows for the same project question.
- Repaired the misplaced Phase 4-B review summary.
- Updated README with the current V2 status.
- No cross-project search, advanced filters, question reuse, or assessment generation was added.

### Phase 5-B: Question Bank Library, Search, and Filters

- Added global question-bank search and item detail APIs.
- Added text, grade, science-domain, unit, and cognitive-category filters.
- Added an owner-aware question-bank library workspace.
- Activated the question-bank card on the V2 task home.
- Added result preview and deletion.
- Updated README with the current V2 status.
- No question reuse, multi-select, assessment generation, or bank sharing was added.

### Phase 5-C: Reuse Question Bank Items in Projects

- Added safe cloning of question-bank items into the current project.
- Added fresh question, part, and attachment IDs.
- Preserved classification, curriculum links, options, marks, and embedded assets.
- Cleared source-project layout and page references.
- Added duplicate protection for the same bank item within a project.
- Added reuse controls and project-state updates in the question-bank library.
- Updated README with the current V2 status.
- No multi-project target picker, bulk reuse, synchronization, or assessment generation was added.

### Phase 6-A: Assessment Blueprint and Test Builder Foundation

- Added persistent SQLite assessment drafts.
- Added assessment blueprint targets for marks, question count, duration, curriculum context, and cognitive distribution.
- Added add/remove operations for question-bank items.
- Added live assessment balance calculations.
- Activated the assessment-builder card and workspace.
- Updated README.
- No automatic selection, ordering, export, answer key, or assessment versioning was added.

### Phase 6-B: Automatic Question Selection and Blueprint Validation

- Added automatic question selection by blueprint.
- Added shortage reporting and strict readiness validation.
- Added builder controls and validation summary.
- Updated README.

### Phase 6-C: Assessment Ordering, Sections, and Manual Marks

- Added persistent assessment sections.
- Added per-question order, section assignment, and mark overrides.
- Added a layout update API and backward-compatible normalization.
- Updated assessment totals to use effective assessment marks.
- Added ordering and section controls to the assessment builder.
- Rewrote README to describe Madarik as an end-to-end Arabic science content and assessment platform.
- No student-paper preview or DOCX/PDF export was added.

### Phase 6-D: Student Paper Preview and Assessment Export Foundation

- Added structured student-paper preview models and service.
- Added section-based question rendering with marks and instructions.
- Added a separate answer-sheet preview.
- Added export-readiness checks.
- Added foundational DOCX and PDF export endpoints.
- Added student preview and export controls to the assessment builder.
- Updated README while preserving the new end-to-end platform description.
- Native formatted DOCX and PDF generation remains deferred.

### Phase 6-E: Native DOCX and PDF Assessment Export

- Replaced text foundations with native DOCX and PDF files.
- Added RTL DOCX structure with sections, marks, answer spaces, and answer sheet.
- Added native PDF generation.
- Added browser file downloads.
- Blocked final export when assessment readiness checks fail.
- Updated README with the current V2 status.
- No school branding or answer-key generation was added.

### Phase 7-A: Differentiated Science Activities Foundation

- Added persistent differentiated activities.
- Added support, core, and extension levels.
- Added create, list, and delete APIs.
- Activated the RTL differentiated-activities workspace.
- Updated README.


### Phase 7-B: Generate Differentiated Activities from Curriculum and Questions

- Added deterministic support, core, and extension activity generation.
- Added optional question-bank context.
- Added distinct scaffolding, challenge, criteria, and timing.
- Added direct persistence of all three activities.
- Added generation controls to the differentiated-activities workspace.
- Updated README.
- No external AI provider or activity export was added.


### Phase 7-C: Differentiated Activity Preview and Export

- Added structured differentiated-activity preview.
- Added activity level, objective, instructions, criteria, materials, and work space.
- Added native RTL DOCX export.
- Added native PDF export.
- Added browser downloads and readiness checks.
- Updated README and closed the differentiated-activities workflow.


### Phase 8-A: Scientific Diagram Data Model and Workspace Foundation

- Added persistent scientific-diagram models and SQLite storage.
- Added six diagram types.
- Added nodes and directed edges.
- Added list, create, and delete APIs.
- Activated a dedicated RTL diagram workspace.
- Updated README.
- No automatic generation or SVG export was added.


### Phase 8-B: Scientific Diagram Preview and SVG Rendering

- Added deterministic positioning for six diagram types.
- Added SVG rendering for nodes, arrows, and edge labels.
- Added browser preview and SVG download.
- Added readiness validation.
- Updated README.
- No PNG/PDF export or drag editing was added.


### Phase 8-C: Scientific Diagram PNG and PDF Export

- Added native PNG conversion from SVG.
- Added native PDF conversion from SVG.
- Added browser downloads.
- Added export-readiness blocking.
- Reused the existing SVG renderer as the single source of truth.
- Updated README and closed the scientific-diagram workflow.


### Phase 9-A: Cloud Source Expansion and OneDrive Foundation

- Added a unified cloud-source model.
- Added Google Drive and OneDrive provider types.
- Added OneDrive and SharePoint URL parsing.
- Added SQLite persistence and cloud-source APIs.
- Added a dedicated RTL workspace.
- Updated README.
- No OAuth, Microsoft Graph, or file synchronization was added.


### Phase 9-B: OneDrive Authentication and Microsoft Graph Adapter

- Added environment-based OneDrive app credentials.
- Added OAuth client-credentials token acquisition.
- Added Microsoft Graph driveItem metadata lookup.
- Added ETag change detection and optional file download.
- Added provider-status and source-sync APIs.
- Added sync and download controls.
- Kept the adapter disabled by default.

### Comprehensive Repair Package

- Restored backward-compatible Google Drive cloud-source contracts.
- Repaired static FastAPI route ordering and resource ownership checks.
- Repaired differentiated activity persistence and assessment preview/export state.
- Fixed frontend imports and missing TypeScript API type imports.
- Replaced unsafe SVG inner HTML rendering.
- Added safe cross-platform export filenames.
- Corrected OneDrive share-link addressing and removed app-only `/me` usage.
- Preserved cloud-source primary keys during upsert.
- Removed duplicate dependency pins and generated SQLite data.
- Updated stale tests and added comprehensive regression coverage.


### Phase 9-C: Cloud Source Refresh, Version History, and Project Intake

- Added persistent cloud-source version history.
- Added content fingerprints, SHA-256 checksums, and version states.
- Added first-version baseline acceptance and manual later-version acceptance.
- Added PDF project intake from accepted downloaded versions.
- Added version, refresh, acceptance, and intake APIs.
- Added version-history and project-intake controls to the RTL workspace.
- Added source-version cleanup when a cloud source is deleted.
- Updated README and closed the cloud-source workflow.


### Phase 9-C Fix 1: Repository Hygiene and Version Fingerprint Stability

- Stabilized cloud-source version identity across metadata-only and downloaded refreshes.
- Kept SHA-256 and file size as verification data instead of download-controlled identity fields.
- Reused and enriched an existing version when the remote ETag and modification timestamp are unchanged.
- Added regression tests for `download=true → false` and `download=false → true`.
- Removed the generated SQLite database from the clean full-source package.
- Updated README status to Phase 9-C Fix 1 and Phase 10-A next.


### Phase 10-A: Release Hardening and End-to-End Acceptance

- Added centralized release metadata for Backend version, channel, and phase.
- Added a safe `/api/health/readiness` endpoint with database, schema, writable-directory, and provider checks.
- Added explicit technical-ready, degraded, and blocked readiness states without exposing secrets or runtime paths.
- Added a deterministic repository audit covering generated files, secrets, version consistency, root-path hygiene, OpenAPI operation IDs, and readiness smoke.
- Added local end-to-end release acceptance across PDF processing, translation, DOCX/PDF export, question bank, assessment, differentiated activities, scientific diagrams, and mocked cloud-source intake.
- Expanded GitHub Actions to run on `feat/madarik-science-platform-v2`, `main`, and pull requests to `main`.
- Added focused Phase 10-A tests before the full Backend suite and Frontend lint/build.
- Preserved the live external-provider Cambridge acceptance and visual DOCX/PDF review as explicit production blockers.


### Phase 10-A Fix 1: PDF Acceptance Stability

- Made PDF question-heading detection tolerant of RTL controls, Arabic-Indic digits, reversed heading fragments, and split extraction lines.
- Counted image XObjects recursively through nested Form XObjects.
- Excluded image masks and alpha soft masks from exported attachment totals.
- Pinned ReportLab to `4.4.9`, the version used by the passing local full suite.
- Added regression tests for nested images, masks, and RTL/split question headings.


### Phase 10-A Fix 2: Deterministic PDF Render Evidence

- Added deterministic PDF render evidence to artifact metadata after question, part, and valid image flowables are queued.
- Kept the original V1 expected-structure manifest fields for backwards compatibility.
- Made new PDFs use render evidence for question, marks, order, and attachment acceptance instead of environment-sensitive text/XObject extraction alone.
- Preserved extractor-based inspection as a fallback for older PDF artifacts.
- Added real generated-PDF regression tests, including deliberately inconsistent reader diagnostics and invalid-image rejection.


### Phase 10-A Fix 3: Frontend Lint and Wiring Closure

- Closed all 9 Frontend ESLint errors reported by GitHub Actions.
- Closed all 3 React Hooks dependency warnings reported by GitHub Actions.
- Replaced five explicit `any` mappings with exact API response interfaces.
- Wired Google Drive source-update acceptance into the linked-source UI.
- Wired scientific diagrams and cloud sources into the science task home instead of leaving dead callback props.
- Removed the unused curriculum type import.
- Stabilized initial question-bank loading without turning filter changes into unintended automatic searches.


### Phase 10-C: Live Gemini Acceptance

- Added a secret-scoped live Gemini workflow triggered only by Phase 10-C implementation changes or manual dispatch.
- Added a redacted acceptance runner that stores hashes, counts, and status metadata only.
- Required the official HTTPS Gemini API host and rejected missing credentials before any provider call.
- Required `external_success` or `corrected_success` and rejected every local fallback path.
- Added Arabic-quality, scientific-fidelity, and approved-glossary validation.
- Added offline tests for success, one correction, fallback rejection, unsafe host rejection, missing-key rejection, report redaction, and workflow safety.
- Kept the full Cambridge translation and visual DOCX/PDF review as open production blockers.
