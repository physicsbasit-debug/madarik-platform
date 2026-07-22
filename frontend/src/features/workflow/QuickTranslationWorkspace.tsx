import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  FileSearch,
  FileText,
  Languages,
  Loader2,
  RotateCcw,
  UploadCloud,
} from "lucide-react";
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

const processingSteps: Array<{
  key: QuickRunStatus;
  title: string;
  description: string;
}> = [
  {
    key: "parsing",
    title: "استخراج بنية الأسئلة",
    description: "تقسيم الورقة إلى أسئلة وأجزاء ودرجات.",
  },
  {
    key: "translating",
    title: "الترجمة العلمية",
    description: "ترجمة الأسئلة مع الحفاظ على الرموز والوحدات.",
  },
  {
    key: "checking",
    title: "فحص الاكتمال",
    description: "مراجعة الأسئلة والدرجات وموانع التصدير.",
  },
];

function stepState(
  step: QuickRunStatus,
  current: QuickRunStatus,
): "waiting" | "active" | "done" | "error" {
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
  const translatedQuestions = activeQuestions.filter(
    (question) => question.translatedText.trim().length > 0,
  );
  const extractionReady = Boolean(extractedText?.isTextBased);
  const canRun =
    extractionReady &&
    apiStatus !== "offline" &&
    !isBusy &&
    quickRunStatus !== "parsing" &&
    quickRunStatus !== "translating" &&
    quickRunStatus !== "checking";
  const canExport = Boolean(
    quickRunStatus === "completed" && projectReadiness?.ready,
  );

  function updateField(
    field: keyof ProjectMetadata,
    value: string,
  ) {
    onMetadataChange({ ...metadata, [field]: value });
  }

  return (
    <main className="quick-translation-workspace" dir="rtl">
      <header className="quick-translation-header">
        <div>
          <span>المسار السريع</span>
          <h1>ترجمة ورقة العلوم</h1>
          <p>
            ارفع الورقة، ثم شغّل الاستخراج والترجمة وفحص الجاهزية
            في عملية واحدة واضحة.
          </p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={onReturnHome}
        >
          <ArrowRight size={18} />
          العودة إلى المهام
        </button>
      </header>

      <section className="quick-translation-grid">
        <div className="quick-translation-main">
          <section className="quick-card">
            <div className="quick-card-heading">
              <UploadCloud size={24} />
              <div>
                <span>الخطوة الأولى</span>
                <h2>بيانات الورقة والملف</h2>
              </div>
            </div>

            <div className="quick-metadata-grid">
              <label>
                <span>المادة</span>
                <input
                  value={metadata.subject}
                  onChange={(event) =>
                    updateField("subject", event.target.value)
                  }
                  placeholder="مثال: الفيزياء"
                />
              </label>
              <label>
                <span>الصف</span>
                <input
                  value={metadata.grade}
                  onChange={(event) =>
                    updateField("grade", event.target.value)
                  }
                  placeholder="مثال: الصف العاشر"
                />
              </label>
              <label className="quick-field-wide">
                <span>عنوان الورقة</span>
                <input
                  value={metadata.paperTitle}
                  onChange={(event) =>
                    updateField("paperTitle", event.target.value)
                  }
                  placeholder="اختبار قصير أو ورقة مراجعة"
                />
              </label>
            </div>

            <label className="quick-upload-zone">
              <input
                type="file"
                accept=".pdf,image/png,image/jpeg,image/webp"
                onChange={(event) =>
                  onFileSelected(event.target.files?.[0] ?? null)
                }
              />
              <FileText size={36} />
              <strong>
                {uploadedFile
                  ? uploadedFile.name
                  : "اختر PDF أو صورة واضحة"}
              </strong>
              <span>
                {uploadedFile
                  ? `${Math.max(1, Math.round(uploadedFile.size / 1024))} كيلوبايت`
                  : "يدعم PDF النصي والمصوّر وPNG وJPG وWEBP"}
              </span>
            </label>

            <div
              className={`quick-extraction-status is-${initialExtractionStatus.phase}`}
            >
              {initialExtractionStatus.phase === "success" ? (
                <CheckCircle2 size={20} />
              ) : initialExtractionStatus.phase === "error" ? (
                <AlertTriangle size={20} />
              ) : isBusy ? (
                <Loader2 size={20} className="spin-icon" />
              ) : (
                <FileSearch size={20} />
              )}
              <div>
                <strong>حالة القراءة الأولية</strong>
                <span>{initialExtractionStatus.message}</span>
              </div>
              {initialExtractionStatus.canRetry ? (
                <button
                  type="button"
                  className="secondary-button compact"
                  onClick={onRetryInitialExtraction}
                >
                  <RotateCcw size={16} />
                  إعادة المحاولة
                </button>
              ) : null}
            </div>
          </section>

          <section className="quick-card">
            <div className="quick-card-heading">
              <Languages size={24} />
              <div>
                <span>الخطوة الثانية</span>
                <h2>تشغيل الترجمة السريعة</h2>
              </div>
            </div>

            <div className="quick-process-steps">
              {processingSteps.map((step) => {
                const state = stepState(step.key, quickRunStatus);
                return (
                  <article
                    key={step.key}
                    className={`quick-process-step is-${state}`}
                  >
                    <div className="quick-process-icon">
                      {state === "done" ? (
                        <CheckCircle2 size={20} />
                      ) : state === "active" ? (
                        <Loader2 size={20} className="spin-icon" />
                      ) : state === "error" ? (
                        <AlertTriangle size={20} />
                      ) : (
                        <span />
                      )}
                    </div>
                    <div>
                      <strong>{step.title}</strong>
                      <p>{step.description}</p>
                    </div>
                  </article>
                );
              })}
            </div>

            <div
              className={`quick-run-message is-${quickRunStatus}`}
            >
              <strong>
                {quickRunStatus === "completed"
                  ? "اكتملت العملية"
                  : quickRunStatus === "error"
                    ? "توقفت العملية"
                    : "حالة العملية"}
              </strong>
              <span>{quickRunMessage}</span>
            </div>

            <button
              type="button"
              className="primary-button quick-run-button"
              disabled={!canRun}
              onClick={onRunQuickTranslation}
            >
              {isBusy ? (
                <Loader2 size={20} className="spin-icon" />
              ) : (
                <Languages size={20} />
              )}
              {quickRunStatus === "completed"
                ? "إعادة تشغيل الترجمة السريعة"
                : "تشغيل الترجمة السريعة"}
            </button>
          </section>
        </div>

        <aside className="quick-translation-summary">
          <section className="quick-card quick-summary-card">
            <div className="quick-card-heading">
              <FileSearch size={22} />
              <div>
                <span>ملخص مباشر</span>
                <h2>حالة الورقة</h2>
              </div>
            </div>

            <dl className="quick-summary-metrics">
              <div>
                <dt>صفحات مقروءة</dt>
                <dd>{extractedText?.pageCount ?? 0}</dd>
              </div>
              <div>
                <dt>الأسئلة</dt>
                <dd>{activeQuestions.length}</dd>
              </div>
              <div>
                <dt>المترجمة</dt>
                <dd>{translatedQuestions.length}</dd>
              </div>
              <div>
                <dt>ملاحظات الجاهزية</dt>
                <dd>{projectReadiness?.issues.length ?? 0}</dd>
              </div>
            </dl>

            {translationBatchSummary ? (
              <div className="quick-batch-summary">
                <strong>ملخص دفعة الترجمة</strong>
                <span>
                  نجاح خارجي:{" "}
                  {translationBatchSummary.externalSuccessCount +
                    translationBatchSummary.correctedSuccessCount}
                </span>
                <span>
                  fallback محلي:{" "}
                  {translationBatchSummary.localFallbackCount}
                </span>
                <span>
                  فشل محفوظ:{" "}
                  {translationBatchSummary.failedSafelyCount}
                </span>
              </div>
            ) : null}

            <div className="quick-sync-note">{lastSyncNote}</div>
          </section>

          <section className="quick-card quick-next-actions">
            <h2>الخطوة التالية</h2>
            <button
              type="button"
              className="primary-button"
              disabled={!canExport}
              onClick={onOpenExport}
            >
              الانتقال إلى التصدير
              <ArrowLeft size={18} />
            </button>
            <button
              type="button"
              className="secondary-button"
              disabled={activeQuestions.length === 0}
              onClick={onOpenProfessionalReview}
            >
              فتح المراجعة الاحترافية
            </button>
            {!canExport && quickRunStatus === "completed" ? (
              <p>
                توجد ملاحظات تمنع التصدير المباشر. افتح المراجعة
                الاحترافية لمعالجتها.
              </p>
            ) : null}
          </section>
        </aside>
      </section>
    </main>
  );
}
