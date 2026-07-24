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
import type { ChangeEvent } from "react";
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

  function updateField(field: keyof ProjectMetadata, value: string) {
    onMetadataChange({ ...metadata, [field]: value });
  }

  return (
    <div className="mdk-simple-process">
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
          <h1>ارفع الملف، ومدارك يتولى الباقي</h1>
          <p>لا إعداد مشروع يدوي، ولا سلسلة أزرار تتكاثر بلا رقابة.</p>
        </div>
      </header>

      <section className="mdk-simple-process-card">
        <div className="mdk-simple-process-card__number">1</div>
        <div className="mdk-simple-process-card__content">
          <div className="mdk-simple-process-card__heading">
            <div>
              <h2>اختر ورقة الاختبار</h2>
              <p>PDF أو صورة واضحة، وسيبدأ استخراج النص تلقائيًا.</p>
            </div>
            {uploadedFile ? (
              <span className="mdk-simple-file-chip">
                <FileText size={17} />
                {uploadedFile.name}
              </span>
            ) : null}
          </div>

          <label className="mdk-simple-upload-zone">
            <input
              type="file"
              accept=".pdf,image/png,image/jpeg,image/webp"
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                onFileSelected(event.target.files?.[0] ?? null)
              }
            />
            <Upload size={30} />
            <strong>{uploadedFile ? "استبدال الملف" : "اختر ملفًا من الجهاز"}</strong>
            <span>أو اسحبه إلى هنا</span>
          </label>

          <div
            className={`mdk-simple-extraction-note is-${initialExtractionStatus.phase}`}
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
                  onChange={(event: ChangeEvent<HTMLInputElement>) => updateField("subject", event.target.value)}
                  placeholder="مثال: الفيزياء"
                />
              </label>
              <label>
                <span>الصف</span>
                <input
                  value={metadata.grade}
                  onChange={(event: ChangeEvent<HTMLInputElement>) => updateField("grade", event.target.value)}
                  placeholder="مثال: الصف العاشر"
                />
              </label>
            </div>
          </details>
        </div>
      </section>

      <section className="mdk-simple-process-card">
        <div className="mdk-simple-process-card__number">2</div>
        <div className="mdk-simple-process-card__content">
          <div className="mdk-simple-process-card__heading">
            <div>
              <h2>جهّز الورقة</h2>
              <p>استخراج الأسئلة والترجمة والفحص في عملية واحدة.</p>
            </div>
            <button
              type="button"
              className="mdk-simple-primary-button is-large"
              onClick={onRunQuickTranslation}
              disabled={!canRun}
            >
              {processing ? <Loader2 size={19} className="mdk-simple-spin" /> : null}
              {processing ? "جارٍ تجهيز الورقة" : "جهّز الورقة"}
              {!processing ? <ArrowLeft size={19} /> : null}
            </button>
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
            {quickRunMessage}
          </div>
        </div>
      </section>

      <section className="mdk-simple-process-card">
        <div className="mdk-simple-process-card__number">3</div>
        <div className="mdk-simple-process-card__content">
          <div className="mdk-simple-process-card__heading">
            <div>
              <h2>راجع النتيجة ثم صدّر</h2>
              <p>تظهر لك الملاحظات فقط، لا كل التفاصيل التقنية.</p>
            </div>
          </div>

          <div className="mdk-simple-result-grid">
            <div>
              <strong>{activeQuestions.length}</strong>
              <span>سؤالًا مستخرجًا</span>
            </div>
            <div>
              <strong>{translatedCount}</strong>
              <span>سؤالًا مترجمًا</span>
            </div>
            <div className={issueCount > 0 ? "needs-attention" : undefined}>
              <strong>{issueCount}</strong>
              <span>ملاحظات للمراجعة</span>
            </div>
          </div>

          {translationAttentionCount > 0 ? (
            <div className="mdk-simple-inline-warning" role="status">
              <AlertTriangle size={18} />
              <span>
                توجد {translationAttentionCount} نتيجة ترجمة تحتاج مراجعة قبل
                الاعتماد النهائي.
              </span>
            </div>
          ) : null}

          <div className="mdk-simple-result-actions">
            {quickRunStatus === "completed" && !readyToExport ? (
              <button
                type="button"
                className="mdk-simple-primary-button"
                onClick={onOpenProfessionalReview}
              >
                مراجعة الملاحظات
                <ArrowLeft size={18} />
              </button>
            ) : null}

            {readyToExport ? (
              <button
                type="button"
                className="mdk-simple-primary-button"
                onClick={onOpenExport}
              >
                تصدير النسخة
                <ArrowLeft size={18} />
              </button>
            ) : null}

            {quickRunStatus === "completed" ? (
              <button
                type="button"
                className="mdk-simple-secondary-button"
                onClick={onOpenProfessionalReview}
              >
                عرض جميع الأسئلة
              </button>
            ) : null}
          </div>

          <small className="mdk-simple-last-note">{lastSyncNote}</small>
        </div>
      </section>
    </div>
  );
}
