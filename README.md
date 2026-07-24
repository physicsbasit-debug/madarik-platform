# منصة مدارك

منصة تعليمية ذكية للعلوم تجمع مصادر المحتوى والمناهج وبنك الأسئلة وبناء الاختبارات والأنشطة والرسوم العلمية، مع مساحة متكاملة لمعالجة أوراق الاختبارات الأجنبية وترجمتها ومراجعتها وتصديرها.

## الحالة الحالية

- معاينة الواجهة الحالية: `Phase 11-B: Unified Workspace Polish and Visual Acceptance`

- الإصدار البرمجي: `2.0.0-rc.2`
- فرع التطوير: `feat/madarik-science-platform-v2`
- القبول الحي للمزود: `Phase 10-C: Live Gemini Acceptance` ناجح
- آخر مرحلة مكتملة: `Phase 11-A: Product UX Realignment`
- المرحلة الحالية: `Phase 11-B: Unified Workspace Polish and Visual Acceptance`
- اختبار مزود خارجي حقيقي: ناجح عبر بوابة Gemini الحية المنقحة
- الحالة التقنية الحالية: صقل الغلاف الموحد وتوحيد رؤوس الوحدات وكثافة المعلومات والاستجابة للشاشات
- الإصدار الإنتاجي: محجوب حتى ترجمة ورقة Cambridge كاملة ومراجعة DOCX/PDF بصريًا

### بوابة الاعتماد الحالية

يُعتمد هذا الفرع فقط بعد نجاح:

- اختبارات Backend الكاملة.
- Frontend lint.
- TypeScript وVite production build.
- فحوص الصلاحيات والملكية.
- فحوص تصدير DOCX وPDF وPNG وSVG.
- فحوص توافق Google Drive وOneDrive دون كسر العقود القديمة.

## ماذا تفعل المنصة؟

تجمع منصة مدارك وحدات العمل العلمي في غلاف واحد: المصادر السحابية، المناهج والدروس، بنك الأسئلة، منشئ الاختبارات، الأنشطة المتمايزة، الرسوم العلمية، ومعالجة أوراق الاختبارات.

وتبقى رحلة معالجة الورقة التعليمية وحدة متكاملة داخل المنصة:

```text
إنشاء مشروع
→ رفع PDF أو صورة
→ استخراج النص أو تشغيل OCR
→ تقسيم الورقة إلى أسئلة وأجزاء
→ مراجعة بنية الأسئلة والدرجات
→ استخراج وربط وقص الرسوم والجداول
→ توليد قاموس مصطلحات
→ ترجمة تعليمية أولية
→ مراجعة اللغة والرموز العلمية
→ اعتماد الأسئلة
→ فحص جاهزية التصدير
→ تصدير DOCX وPDF
```

## الوظائف الرئيسية

- رفع ملفات PDF والصور التعليمية.
- استخراج النص من PDF النصي.
- تشغيل OCR على الصور والملفات المصورة المدعومة.
- تقسيم النص إلى أسئلة وأجزاء وخيارات.
- دعم الأسئلة متعددة الأجزاء.
- ربط الأصول البصرية بالأسئلة.
- قص الرسوم والجداول من صفحات PDF.
- إنشاء قاموس مصطلحات ومراجعته.
- دعم الترجمة عبر:
  - Gemini `generateContent`
  - OpenAI Responses API
  - مزودات OpenAI-compatible
- استخدام fallback محلي واضح عند تعذر المزود الخارجي.
- منع اعتماد ترجمة fallback بوصفها ترجمة نهائية.
- فحص جودة اللغة العربية وبقايا النثر الإنجليزي.
- حماية الرموز والقيم والوحدات والمعادلات العلمية.
- محاولة تصحيح خارجية واحدة عند اكتشاف مخالفة.
- مراجعة الأسئلة وتعديلها وحذفها واستعادتها وترتيبها.
- إجراءات جماعية لحالات المراجعة.
- فحص جاهزية التصدير وموانع القبول.
- تصدير نسخ الطالب بصيغتي DOCX وPDF مع RTL.
- حفظ المشاريع في SQLite.
- تصدير واستيراد Snapshot بصيغة JSON.
- حسابات مستخدمين وأدوار وصلاحيات أولية.
- أدوات تحليل تربوي وجودة تعليمية.

## معايير الترجمة العلمية

يسمح حارس الجودة بالرموز والمصطلحات العلمية الضرورية مثل:

```text
V = IR
I = 2 A
5 Ω
CMBR
Fig. 1.1
5.0 × 10⁻⁴
```

ويرفض النصوص المختلطة غير المفسرة مثل:

```text
فسّر why the current decreases
```

كما يتحقق مسار القبول من:

- سلامة القيم الرقمية.
- سلامة الوحدات والرموز.
- سلامة الدرجات.
- احترام القاموس المعتمد.
- عدم اعتماد ترجمة fallback.
- تسجيل مصدر الترجمة الخارجي عند نجاح المزود.

## التقنيات المستخدمة

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- PyMuPDF
- pypdf
- Tesseract OCR
- python-docx
- ReportLab
- httpx
- pytest

### Frontend

- React
- TypeScript
- Vite
- ESLint
- Lucide React

## بنية المشروع

```text
madarik-platform/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
├── RUN_PHASE4_B1_TESTS.sh
├── RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
└── README.md
```

## تشغيل Backend

من جذر المشروع:

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

على Windows:

```powershell
cd backend

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> يحتاج OCR إلى تثبيت Tesseract في نظام التشغيل، وليس داخل بيئة Python فقط.

## تشغيل Frontend

من جذر المشروع:

```bash
cd frontend

npm ci
npm run dev -- --host 0.0.0.0
```

لإنشاء نسخة إنتاج:

```bash
cd frontend

npm run lint
npm run build
```

## إعداد مزود الذكاء الاصطناعي

انسخ ملف البيئة النموذجي:

```bash
cd backend

cp .env.example .env
```

ثم أدخل داخل `backend/.env`:

- اسم المزود.
- مفتاح API صالح.
- معرّف نموذج مدعوم حاليًا من المزود.
- عنوان API عند الحاجة.

راجع الملف:

```text
backend/.env.example
```

### قواعد أمنية

- لا تحفظ مفاتيح API داخل Git.
- لا ترسل المفتاح في المحادثات أو السجلات.
- لا تستخدم اسم نموذج تخمينيًا.
- لا تعتمد نتيجة fallback بوصفها ترجمة خارجية.
- لا تطبع الاستجابة الخام في الاختبار الحي.

## الاختبارات

### بوابة Phase 4-B1

من جذر المشروع:

```bash
chmod +x RUN_PHASE4_B1_TESTS.sh
./RUN_PHASE4_B1_TESTS.sh
```

تشمل البوابة:

- فحص Python syntax.
- اختبارات Backend المركزة.
- Frontend lint.
- Frontend production build.

### اختبارات Backend الكاملة

```bash
cd backend

source .venv/bin/activate
python -m pytest -q
```

### الاختبار الحي

بعد إعداد مزود ومفتاح ونموذج صالحين:

```bash
cd /path/to/madarik-platform

source backend/.venv/bin/activate

python RUN_PHASE4_B1_LIVE_ACCEPTANCE.py
```

الاختبار الحي لا يطبع المفتاح أو الحمولة السرية.

## بوابة القبول الإنتاجي

لا تعد Phase 4-B1 مغلقة إنتاجيًا إلا بعد تحقق جميع الشروط التالية:

- استخدام مزود ذكاء اصطناعي خارجي حقيقي.
- ترجمة ورقة Cambridge كاملة.
- التأكد من أن الناتج ليس fallback.
- عدم بقاء نثر إنجليزي غير مفسر في النسخة العربية.
- سلامة القيم والرموز والوحدات والأسس العلمية.
- سلامة الرسوم والأصول البصرية في DOCX وPDF.
- اتساق الدرجات وسياسة العلامات.
- اجتياز مراجعة المعلم.
- وصول تقرير الرحلة الكاملة إلى حالة قبول صحيحة.

## الحالة غير المنجزة

- اختبار Gemini الحي المصغر اجتاز GitHub Actions بنجاح.
- القبول النهائي لورقة Cambridge الكاملة لم يُغلق بعد.
- المشروع لم يُعلن نسخة إنتاج نهائية.
- المتبقي للإنتاج هو ترجمة ورقة Cambridge كاملة ومراجعة DOCX وPDF بصريًا.

## الوثائق

توجد وثائق المراحل والقبول داخل مجلد:

```text
docs/
```

وثيقة Phase 4-B1 الأساسية:

```text
docs/PHASE_4_B1_REAL_AI_TRANSLATION_ACCEPTANCE.md
```

## ملاحظة التطوير

يجب أن تمر التعديلات الجديدة عبر الاختبارات المركزة والاختبارات الكاملة وبناء الواجهة قبل الدمج. أي تحسين لا يدخل في نطاق الإغلاق الحالي يُرحّل إلى إصدار لاحق بدل توسيع النسخة المرشحة بلا نهاية.

## ما هي منصة مدارك؟

**منصة مدارك** هي منصة عربية متخصصة في تحويل المحتوى والاختبارات العلمية
الأجنبية إلى موارد تعليمية عربية قابلة للمراجعة وإعادة الاستخدام وبناء
التقويمات منها. لا تتعامل المنصة مع الترجمة بوصفها استبدال كلمات فقط، بل
تدير دورة العمل التعليمية كاملة من المصدر حتى الاختبار النهائي.

تبدأ الرحلة من رفع ملف PDF أو ربط مصدر سحابي، ثم استخراج النص وتقسيمه إلى
أسئلة وأجزاء، وإنشاء قاموس علمي، وترجمة المحتوى مع الحفاظ على الرموز
والمعادلات والرسوم. بعد ذلك يراجع المعلم السؤال، ويصنفه معرفيًا، ويربطه
بالصف والمادة والوحدة والدرس ونواتج التعلم.

الأسئلة المعتمدة تُحفظ في **بنك أسئلة دائم** يمكن البحث فيه وتصفيته وإعادة
استخدام عناصره داخل مشاريع أخرى. ومن البنك ينتقل المستخدم إلى **منشئ
الاختبارات** الذي يعتمد جدول مواصفات يوازن بين المعرفة والتطبيق
والاستدلال، ويختار الأسئلة آليًا أو يدويًا، ثم يسمح بترتيبها داخل أقسام
وتعديل درجاتها قبل التصدير في المراحل اللاحقة.

### الفكرة الجديدة للبرنامج

الفكرة الجديدة هي أن مدارك لم تعد مجرد أداة ترجمة اختبارات، بل أصبحت
**منظومة إدارة محتوى وتقويم علمي** تربط خمسة مسارات في مكان واحد:

1. استيراد المصادر العلمية ومتابعة نسخها.
2. الترجمة العلمية والمراجعة البصرية واللغوية.
3. التصنيف المعرفي والربط بالمنهج ونواتج التعلم.
4. بناء بنك أسئلة منظم وقابل لإعادة الاستخدام.
5. إنشاء اختبارات متوازنة وفق جدول مواصفات واضح.

تستهدف المنصة معلمي العلوم والفيزياء والكيمياء والأحياء، والمشرفين
التربويين، وفرق إعداد الاختبارات والمحتوى العربي. وتبقى قرارات الاعتماد
النهائية بيد المعلم؛ فالاختيار والتصنيف الآليان أدوات مساعدة وليسا بديلًا
عن الحكم التربوي.

## Madarik Science Platform V2 Status

Development branch:

```text
feat/madarik-science-platform-v2
```

Completed V2 phases:

- Phase 0-A: Scope, architecture, and data contracts.
- Phase 0-B: Task-oriented home.
- Phase 1: Quick translation workflow.
- Phase 2: Curriculum structure for grades 1–12.
- Phase 3-A: Google Drive source foundation.
- Phase 3-B: Curriculum source persistence.
- Phase 3-C: Source refresh detection.
- Phase 3-D: Source Version History and Manual Update Acceptance.
- Phase 4-A: Science Question Classification Foundation.
- Phase 4-B: Curriculum Linking and Classification Review.
- Phase 5-A: Question Bank Data Model and Persistence.
- Phase 5-B: Question Bank Library, Search, and Filters.
- Phase 5-C: Reuse Question Bank Items in Projects.
- Phase 6-A: Assessment Blueprint and Test Builder Foundation.
- Phase 6-B: Automatic Question Selection and Blueprint Validation.
- Phase 6-C: Assessment Ordering, Sections, and Manual Marks.
- Phase 6-D: Student Paper Preview and Assessment Export Foundation.
- Phase 6-E: Native DOCX and PDF Assessment Export.
- Phase 7-A: Differentiated Science Activities Foundation.
- Phase 7-B: Generate Differentiated Activities from Curriculum and Questions.
- Phase 7-C: Differentiated Activity Preview and Export.
- Phase 8-A: Scientific Diagram Data Model and Workspace Foundation.
- Phase 8-B: Scientific Diagram Preview and SVG Rendering.
- Phase 8-C: Scientific Diagram PNG and PDF Export.
- Phase 9-A: Cloud Source Expansion and OneDrive Foundation.
- Phase 9-B: OneDrive Authentication and Microsoft Graph Adapter.
- Phase 9-C: Cloud Source Refresh, Version History, and Project Intake.
- Phase 10-A: Release Hardening and End-to-End Acceptance.
- Phase 10-B: Final Release Candidate Consolidation and Sign-off.
- Phase 10-C: Live Gemini Acceptance.
- Phase 11-A: Product UX Realignment.
- Phase 11-B: Unified Workspace Polish and Visual Acceptance.

Phase 9-C adds:

- persistent cloud-source version history;
- content fingerprints and SHA-256 checksums;
- first-version baseline acceptance;
- manual acceptance for later versions;
- accepted, detected, and superseded states;
- PDF project intake from an accepted downloaded version;
- creation of a new project when no target project is selected;
- ownership-safe version, acceptance, and intake APIs.

The cloud-source workflow is now functionally closed.

Phase 9-C Fix 1 adds:

- stable version identity independent of the download flag;
- checksum enrichment without creating a false cloud-source version;
- regression coverage for download-to-metadata and metadata-to-download refreshes;
- repository-package cleanup for the generated SQLite file.

Phase 10-A adds:

- a safe `/api/health/readiness` runtime report;
- centralized release version and phase metadata;
- SQLite schema, writable-data, export-directory, and provider checks;
- a repository, secret, version, OpenAPI, and readiness audit script;
- local end-to-end acceptance across PDF intake, parsing, translation, export,
  question bank, assessment, differentiated activities, scientific diagrams,
  and mocked cloud-source intake;
- GitHub Actions coverage for the active development branch and `main` pull
  requests;
- explicit separation between technical readiness and the remaining live
  external-provider acceptance.

The technical release gate is now defined. Production release remains blocked
until a real external provider translates a full Cambridge paper and the DOCX
and PDF outputs pass visual review.

Phase 10-B consolidates the final release candidate:

- version `2.0.0-rc.2` is unified across Backend, Frontend, lockfile, README, and release status;
- one active release-gate workflow runs preflight, Backend, Frontend, and whitespace checks;
- a machine-readable final-release status keeps production release and tagging blocked;
- the RC preflight validates repository hygiene, secrets, versions, workflow identity, OpenAPI, and readiness;
- the technical candidate is ready for CI, while live external-provider acceptance and visual DOCX/PDF review remain mandatory.


Phase 10-C prepares the redacted live Gemini acceptance:

- reads Gemini configuration only from GitHub Actions secrets;
- requires the official HTTPS Gemini API host before sending the request;
- executes a real scientific translation without printing the key, prompt,
  source text, translated text, provider note, or raw response payload;
- rejects local fallback and requires external-success or corrected-success;
- verifies Arabic quality, scientific fidelity, and approved glossary terms;
- uploads a redacted JSON evidence artifact containing status, counts, and
  SHA-256 hashes only;
- keeps the full Cambridge and visual DOCX/PDF blockers open after the smoke
  test, because one live question is evidence of connectivity, not sainthood.


Phase 11-A realigns the product interface:

- replaces the old task page with a platform dashboard and persistent navigation;
- exposes cloud sources, curriculum, question bank, assessments, activities,
  diagrams, quick translation, and professional paper processing as first-class modules;
- keeps the active project, connection state, project actions, and account access
  visible throughout the platform;
- turns the import-review-export journey into a contextual workspace inside the
  wider product shell;
- preserves Backend contracts, storage, translation, OCR, and export behavior.

## نشر معاينة Phase 11-A على GitHub Pages

تنشر الواجهة الجديدة عبر Workflow مستقل:

```text
.github/workflows/deploy-phase11a-preview.yml
```

ويجب ضبط مصدر Pages على `GitHub Actions`. يبني Workflow مجلد `frontend/dist` عبر `vite build --base=/madarik-platform/`،
ثم يرفعه وينشره على رابط المستودع نفسه دون تغيير إعداد التطوير المحلي.
عنوان Backend الاختياري يقرأ من Repository Variable باسم:

```text
MADARIK_API_BASE_URL
```


Phase 11-B polishes the unified workspace:

- reduces sidebar and dashboard density for medium screens;
- clarifies the top-bar overflow action and constrains content width;
- unifies module headers across all first-class workspaces;
- improves keyboard focus states and responsive breakpoints;
- preserves all data and Backend contracts.
