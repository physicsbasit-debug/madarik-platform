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
