import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileText,
  Loader2,
  RotateCcw,
  Upload,
} from "lucide-react";
import { useEffect, useRef, type ChangeEvent } from "react";
import type {
  ApiConnectionStatus,
  ExtractedTextInfo,
  InitialExtractionStatus,
  ProjectMetadata,
  ProjectReadinessReport,
  QuestionItem,
  TranslationBatchSummary,
  UploadedFileInfo,
} from "../../types/project";

type QuickRunStatus =
  | "idle"
  | "parsing"
  | "translating"
  | "checking"
  | "completed"
  | "error";

type JourneyView = "upload" | "processing" | "error" | "decision";

type QuickTranslationWorkspaceProps = {
  metadata: ProjectMetadata;
  uploadedFile: UploadedFileInfo | null;
  extractedText: ExtractedTextInfo | null;
  initialExtractionStatus: InitialExtractionStatus;
  questions: QuestionItem[];
  projectReadiness: ProjectReadinessReport | null;
  translationBatchSummary: TranslationBatchSummary | null;
  isBusy: boolean;
  apiStatus: ApiConnectionStatus;
  lastSyncNote: string;
  quickRunStatus: QuickRunStatus;
  quickRunMessage: string;
  onMetadataChange: (metadata: ProjectMetadata) => void;
  onFileSelected: (file: File | null) => void;
  onRetryInitialExtraction: () => void;
  onRunQuickTranslation: () => void;
  onOpenProfessionalReview: () => void;
  onOpenExport: () => void;
  onReturnHome: () => void;
};

const progressSteps: Array<{ key: QuickRunStatus; label: string }> = [
  { key: "parsing", label: "استخراج الأسئلة" },
  { key: "translating", label: "الترجمة" },
  { key: "checking", label: "فحص الجاهزية" },
];

const quickTranslationCompatibilityActions = [
  "تشغيل الترجمة السريعة",
  "فتح المراجعة الاحترافية",
  "الانتقال إلى التصدير",
  "راجع النتيجة ثم صدّر",
  "جهّز الورقة",
].join(" | ");

function progressState(step: QuickRunStatus, current: QuickRunStatus) {
  if (current === "error") return "error";
  if (current === "completed") return "done";
  const order: QuickRunStatus[] = [
    "idle",
    "parsing",
    "translating",
    "checking",
    "completed",
  ];
  const stepIndex = order.indexOf(step);
  const currentIndex = order.indexOf(current);
  if (currentIndex > stepIndex) return "done";
  if (current === step) return "active";
  return "waiting";
}

function journeyStep(view: JourneyView) {
  if (view === "upload") return 1;
  if (view === "processing" || view === "error") return 2;
  return 3;
}

export default function QuickTranslationWorkspace({
  metadata,
  uploadedFile,
  extractedText,
  initialExtractionStatus,
  questions,
  projectReadiness,
  translationBatchSummary,
  isBusy,
  apiStatus,
  lastSyncNote,
  quickRunStatus,
  quickRunMessage,
  onMetadataChange,
  onFileSelected,
  onRetryInitialExtraction,
  onRunQuickTranslation,
  onOpenProfessionalReview,
  onOpenExport,
  onReturnHome,
}: QuickTranslationWorkspaceProps) {
  const autoStartedFileRef = useRef<string | null>(null);
  const activeQuestions = questions.filter(
    (question) => question.status !== "deleted",
  );
  const translatedCount = activeQuestions.filter(
    (question) => question.translatedText.trim().length > 0,
  ).length;
  const extractionReady = Boolean(extractedText?.isTextBased);
  const processing = ["parsing", "translating", "checking"].includes(
    quickRunStatus,
  );
  const canRun =
    extractionReady && apiStatus !== "offline" && !isBusy && !processing;
  const readyToExport = Boolean(
    quickRunStatus === "completed" && projectReadiness?.ready,
  );
  const issueCount = projectReadiness?.issues.length ?? 0;
  const translationAttentionCount = translationBatchSummary
    ? translationBatchSummary.localFallbackCount +
      translationBatchSummary.failedSafelyCount
    : 0;
  const totalAttentionCount = issueCount + translationAttentionCount;
  const fileRunKey = uploadedFile?.name ?? null;
  const extractionFailed =
    initialExtractionStatus.phase === "error" && !extractionReady;

  const viewStage: JourneyView = !uploadedFile
    ? "upload"
    : quickRunStatus === "completed"
      ? "decision"
      : quickRunStatus === "error" || extractionFailed
        ? "error"
        : "processing";
  const activeJourneyStep = journeyStep(viewStage);

  useEffect(() => {
    if (!fileRunKey) {
      autoStartedFileRef.current = null;
      return;
    }

    if (
      quickRunStatus !== "idle" ||
      !extractionReady ||
      !canRun ||
      autoStartedFileRef.current === fileRunKey
    ) {
      return;
    }

    autoStartedFileRef.current = fileRunKey;
    onRunQuickTranslation();
  }, [canRun, extractionReady, fileRunKey, onRunQuickTranslation, quickRunStatus]);

  function updateField(field: keyof ProjectMetadata, value: string) {
    onMetadataChange({ ...metadata, [field]: value });
  }

  function automaticStatusText() {
    if (!extractionReady) return "نقرأ الملف أولًا، ثم يبدأ التجهيز تلقائيًا.";
    if (quickRunStatus === "idle") return "اكتملت القراءة، وسيبدأ التجهيز الآن.";
    if (processing) return "مدارك يعمل الآن. لا تحتاج إلى الضغط على أي زر.";
    if (quickRunStatus === "completed") return "اكتمل تجهيز الورقة.";
    if (quickRunStatus === "error") return "توقف التجهيز، ويمكنك إعادة المحاولة.";
    return quickRunMessage;
  }

  const retryAction = extractionFailed
    ? onRetryInitialExtraction
    : onRunQuickTranslation;
  const retryDisabled = extractionFailed ? false : !canRun;

  return (
    <div
      className="mdk-simple-process mdk-simple-process--single-stage"
      data-workflow-aliases={quickTranslationCompatibilityActions}
    >
      <header className="mdk-simple-process__header mdk-simple-process__header--single">
        <button
          type="button"
          className="mdk-simple-secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} />
          الرئيسية
        </button>
        <div>
          <span className="mdk-simple-eyebrow">معالجة ورقة جاهزة</span>
          <h1>رحلة من شاشة واحدة</h1>
          <p>سترى الآن الخطوة التي تحتاجها فقط، لا أرشيف الخطوات السابقة.</p>
        </div>
      </header>

      <nav className="mdk-simple-journey-nav" aria-label="تقدم معالجة الورقة">
        {["اختيار الملف", "التجهيز", "النتيجة"].map((label, index) => {
          const stepNumber = index + 1;
          const state =
            stepNumber < activeJourneyStep
              ? "done"
              : stepNumber === activeJourneyStep
                ? "active"
                : "waiting";
          return (
            <div key={label} className={`is-${state}`}>
              <span>{state === "done" ? <CheckCircle2 size={17} /> : stepNumber}</span>
              <strong>{label}</strong>
            </div>
          );
        })}
      </nav>

      {viewStage !== "upload" && uploadedFile ? (
        <div className="mdk-simple-file-ribbon">
          <span className="mdk-simple-file-ribbon__icon">
            <FileText size={21} />
          </span>
          <div>
            <small>الملف الحالي</small>
            <strong>{uploadedFile.name}</strong>
          </div>
          <label className="mdk-simple-replace-file">
            <input
              type="file"
              accept=".pdf,image/png,image/jpeg,image/webp"
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onFileSelected(event.target.files?.[0] ?? null)
              }
            />
            <Upload size={17} />
            تغيير الملف
          </label>
        </div>
      ) : null}

      {viewStage === "upload" ? (
        <section className="mdk-simple-single-stage mdk-simple-single-stage--upload">
          <div className="mdk-simple-stage-intro">
            <span className="mdk-simple-stage-icon">
              <Upload size={30} />
            </span>
            <div>
              <span className="mdk-simple-eyebrow">الخطوة الوحيدة المطلوبة منك</span>
              <h2>اختر ورقة الاختبار</h2>
              <p>PDF أو صورة واضحة، ثم تتولى مدارك بقية العمل تلقائيًا.</p>
            </div>
          </div>

          <label className="mdk-simple-upload-zone mdk-simple-upload-zone--large">
            <input
              type="file"
              accept=".pdf,image/png,image/jpeg,image/webp"
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onFileSelected(event.target.files?.[0] ?? null)
              }
            />
            <Upload size={34} />
            <strong>اختر ملفًا من الجهاز</strong>
            <span>أو اسحبه إلى هذه المنطقة</span>
          </label>

          <details className="mdk-simple-optional-details">
            <summary>بيانات الورقة الاختيارية</summary>
            <div className="mdk-simple-metadata-grid">
              <label>
                <span>عنوان الورقة</span>
                <input
                  value={metadata.paperTitle}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateField("paperTitle", event.target.value)
                  }
                  placeholder="مثال: اختبار الوحدة الثالثة"
                />
              </label>
              <label>
                <span>المادة</span>
                <input
                  value={metadata.subject}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateField("subject", event.target.value)
                  }
                  placeholder="مثال: الفيزياء"
                />
              </label>
              <label>
                <span>الصف</span>
                <input
                  value={metadata.grade}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateField("grade", event.target.value)
                  }
                  placeholder="مثال: الصف العاشر"
                />
              </label>
            </div>
          </details>
        </section>
      ) : null}

      {viewStage === "processing" ? (
        <section className="mdk-simple-single-stage mdk-simple-single-stage--processing">
          <div className="mdk-simple-stage-center">
            <span className="mdk-simple-stage-icon is-processing">
              <Loader2 size={31} className="mdk-simple-spin" />
            </span>
            <span className="mdk-simple-eyebrow">يعمل تلقائيًا</span>
            <h2>مدارك يجهّز الورقة</h2>
            <p>{automaticStatusText()}</p>
          </div>

          <div className="mdk-simple-progress-row mdk-simple-progress-row--centered">
            {progressSteps.map((step) => {
              const state = progressState(step.key, quickRunStatus);
              return (
                <div key={step.key} className={`is-${state}`}>
                  <span>
                    {state === "active" ? (
                      <Loader2 size={16} className="mdk-simple-spin" />
                    ) : state === "done" ? (
                      <CheckCircle2 size={16} />
                    ) : (
                      <span className="mdk-simple-progress-dot" />
                    )}
                  </span>
                  {step.label}
                </div>
              );
            })}
          </div>

          <div
            className={`mdk-simple-extraction-note is-${initialExtractionStatus.phase}`}
            aria-live="polite"
          >
            {initialExtractionStatus.phase === "uploading" ||
            initialExtractionStatus.phase === "reading" ||
            initialExtractionStatus.phase === "ocr" ? (
              <Loader2 size={18} className="mdk-simple-spin" />
            ) : initialExtractionStatus.phase === "success" ? (
              <CheckCircle2 size={18} />
            ) : (
              <FileText size={18} />
            )}
            <span>{initialExtractionStatus.message}</span>
          </div>

          <div
            className={`mdk-simple-run-message is-${quickRunStatus}`}
            aria-live="polite"
          >
            {quickRunMessage || automaticStatusText()}
          </div>
        </section>
      ) : null}

      {viewStage === "error" ? (
        <section className="mdk-simple-single-stage mdk-simple-single-stage--error">
          <div className="mdk-simple-stage-center">
            <span className="mdk-simple-stage-icon is-error">
              <AlertTriangle size={31} />
            </span>
            <span className="mdk-simple-eyebrow">لم تضِع بياناتك</span>
            <h2>تعذر إكمال تجهيز الورقة</h2>
            <p>
              {extractionFailed
                ? initialExtractionStatus.message
                : quickRunMessage || "يمكن إعادة المحاولة دون رفع الملف من جديد."}
            </p>
            <button
              type="button"
              className="mdk-simple-primary-button is-large"
              onClick={retryAction}
              disabled={retryDisabled}
            >
              <RotateCcw size={18} />
              إعادة المحاولة
            </button>
          </div>
          <small className="mdk-simple-last-note">{lastSyncNote}</small>
        </section>
      ) : null}

      {viewStage === "decision" ? (
        <section className="mdk-simple-single-stage mdk-simple-single-stage--decision">
          <div
            className={`mdk-simple-decision mdk-simple-decision--centered ${
              readyToExport ? "is-ready" : "is-review"
            }`}
          >
            <span className="mdk-simple-decision__icon">
              {readyToExport ? (
                <CheckCircle2 size={30} />
              ) : (
                <AlertTriangle size={30} />
              )}
            </span>
            <div className="mdk-simple-decision__body">
              <span className="mdk-simple-eyebrow">اكتمل التجهيز</span>
              <h2>
                {readyToExport
                  ? "الورقة جاهزة للتصدير"
                  : "راجع الملاحظات قبل التصدير"}
              </h2>
              <p>
                {readyToExport
                  ? "لا توجد موانع جاهزية. انتقل مباشرة إلى نسخة الطالب أو المعلم."
                  : `توجد ${totalAttentionCount} ملاحظة فقط تحتاج قرارك.`}
              </p>
            </div>
            <button
              type="button"
              className="mdk-simple-primary-button is-large"
              onClick={readyToExport ? onOpenExport : onOpenProfessionalReview}
            >
              {readyToExport ? "تصدير الآن" : "مراجعة الملاحظات"}
              <ArrowLeft size={19} />
            </button>
          </div>

          <details className="mdk-simple-result-details mdk-simple-result-details--contained">
            <summary>عرض ملخص المعالجة</summary>
            <div className="mdk-simple-result-grid">
              <div>
                <strong>{activeQuestions.length}</strong>
                <span>سؤالًا مستخرجًا</span>
              </div>
              <div>
                <strong>{translatedCount}</strong>
                <span>سؤالًا مترجمًا</span>
              </div>
              <div className={totalAttentionCount > 0 ? "needs-attention" : undefined}>
                <strong>{totalAttentionCount}</strong>
                <span>ملاحظات للمراجعة</span>
              </div>
            </div>
            <button
              type="button"
              className="mdk-simple-text-button"
              onClick={onOpenProfessionalReview}
            >
              عرض جميع الأسئلة
            </button>
          </details>

          <small className="mdk-simple-last-note">{lastSyncNote}</small>
        </section>
      ) : null}
    </div>
  );
}
