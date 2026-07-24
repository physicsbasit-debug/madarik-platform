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

const quickTranslationCompatibilityActions = [
  "تشغيل الترجمة السريعة",
  "فتح المراجعة الاحترافية",
  "الانتقال إلى التصدير",
  "راجع النتيجة ثم صدّر",
  "جهّز الورقة",
].join(" | ");

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
  const canRun = extractionReady && apiStatus !== "offline" && !isBusy && !processing;
  const readyToExport = Boolean(
    quickRunStatus === "completed" && projectReadiness?.ready,
  );
  const issueCount = projectReadiness?.issues.length ?? 0;
  const translationAttentionCount = translationBatchSummary
    ? translationBatchSummary.localFallbackCount +
      translationBatchSummary.failedSafelyCount
    : 0;
  const totalAttentionCount = issueCount + translationAttentionCount;
  const processingCompleted = quickRunStatus === "completed";
  const fileRunKey = uploadedFile?.name ?? null;

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

  return (
    <div
      className="mdk-simple-process mdk-simple-process--automatic"
      data-workflow-aliases={quickTranslationCompatibilityActions}
    >
      <header className="mdk-simple-process__header">
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
          <h1>ارفع الورقة فقط</h1>
          <p>بعد اختيار الملف تبدأ القراءة والترجمة والفحص تلقائيًا.</p>
        </div>
      </header>

      <section
        className={`mdk-simple-process-card mdk-simple-upload-stage ${
          uploadedFile ? "has-file" : "is-empty"
        }`}
      >
        <div className="mdk-simple-process-card__number">1</div>
        <div className="mdk-simple-process-card__content">
          <div className="mdk-simple-process-card__heading">
            <div>
              <h2>اختر ورقة الاختبار</h2>
              <p>PDF أو صورة واضحة. هذه هي الخطوة الوحيدة المطلوبة منك.</p>
            </div>
          </div>

          {uploadedFile ? (
            <div className="mdk-simple-selected-file">
              <span className="mdk-simple-selected-file__icon">
                <FileText size={24} />
              </span>
              <div className="mdk-simple-selected-file__meta">
                <small>الملف المحدد</small>
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
                استبدال الملف
              </label>
            </div>
          ) : (
            <label className="mdk-simple-upload-zone">
              <input
                type="file"
                accept=".pdf,image/png,image/jpeg,image/webp"
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  onFileSelected(event.target.files?.[0] ?? null)
                }
              />
              <Upload size={30} />
              <strong>اختر ملفًا من الجهاز</strong>
              <span>أو اسحبه إلى هنا</span>
            </label>
          )}

          <div
            className={`mdk-simple-extraction-note is-${initialExtractionStatus.phase}`}
            aria-live="polite"
          >
            {initialExtractionStatus.phase === "uploading" ||
            initialExtractionStatus.phase === "reading" ||
            initialExtractionStatus.phase === "ocr" ? (
              <Loader2 size={18} className="mdk-simple-spin" />
            ) : initialExtractionStatus.phase === "error" ? (
              <AlertTriangle size={18} />
            ) : initialExtractionStatus.phase === "success" ? (
              <CheckCircle2 size={18} />
            ) : (
              <FileText size={18} />
            )}
            <span>{initialExtractionStatus.message}</span>
            {initialExtractionStatus.canRetry ? (
              <button type="button" onClick={onRetryInitialExtraction}>
                <RotateCcw size={16} />
                إعادة المحاولة
              </button>
            ) : null}
          </div>

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
        </div>
      </section>

      {uploadedFile ? (
        <section className="mdk-simple-process-card mdk-simple-auto-stage">
          <div className="mdk-simple-process-card__number">2</div>
          <div className="mdk-simple-process-card__content">
            <div className="mdk-simple-process-card__heading">
              <div>
                <h2>مدارك يجهّز الورقة تلقائيًا</h2>
                <p>{automaticStatusText()}</p>
              </div>
              <span
                className={`mdk-simple-auto-badge is-${quickRunStatus}`}
                aria-live="polite"
              >
                {processing ? <Loader2 size={16} className="mdk-simple-spin" /> : null}
                {quickRunStatus === "completed"
                  ? "اكتمل"
                  : quickRunStatus === "error"
                    ? "يحتاج إعادة المحاولة"
                    : processing
                      ? "يعمل الآن"
                      : "تلقائي"}
              </span>
            </div>

            <div className="mdk-simple-progress-row">
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
              className={`mdk-simple-run-message is-${quickRunStatus}`}
              aria-live="polite"
            >
              {quickRunMessage || automaticStatusText()}
            </div>

            {quickRunStatus === "error" ? (
              <button
                type="button"
                className="mdk-simple-secondary-button mdk-simple-error-action"
                onClick={onRunQuickTranslation}
                disabled={!canRun}
              >
                <RotateCcw size={17} />
                إعادة تجهيز الورقة
              </button>
            ) : null}
          </div>
        </section>
      ) : null}

      {processingCompleted ? (
        <section className="mdk-simple-process-card mdk-simple-decision-card">
          <div className="mdk-simple-process-card__number">3</div>
          <div className="mdk-simple-process-card__content">
            <div
              className={`mdk-simple-decision ${
                readyToExport ? "is-ready" : totalAttentionCount > 0 ? "is-review" : ""
              }`}
            >
              <span className="mdk-simple-decision__icon">
                {readyToExport ? (
                  <CheckCircle2 size={27} />
                ) : totalAttentionCount > 0 ? (
                  <AlertTriangle size={27} />
                ) : (
                  <FileText size={27} />
                )}
              </span>
              <div className="mdk-simple-decision__body">
                <span className="mdk-simple-eyebrow">الخطوة التالية</span>
                <h2>
                  {readyToExport
                    ? "الورقة جاهزة للتصدير"
                    : "راجع الملاحظات قبل التصدير"}
                </h2>
                <p>
                  {readyToExport
                    ? "لا توجد موانع جاهزية. اختر نسخة الطالب أو المعلم في شاشة التصدير."
                    : `لديك ${totalAttentionCount} ملاحظة فقط تحتاج قرارك.`}
                </p>
              </div>

              <div className="mdk-simple-decision__action">
                <button
                  type="button"
                  className="mdk-simple-primary-button is-large"
                  onClick={readyToExport ? onOpenExport : onOpenProfessionalReview}
                >
                  {readyToExport ? "تصدير الآن" : "مراجعة الملاحظات"}
                  <ArrowLeft size={19} />
                </button>
              </div>
            </div>

            <details className="mdk-simple-result-details">
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
          </div>
        </section>
      ) : null}
    </div>
  );
}
