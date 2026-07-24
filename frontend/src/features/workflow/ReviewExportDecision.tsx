import {
  AlertTriangle,
  CheckCircle2,
  Download,
  Eye,
  ListChecks,
  LockKeyhole,
} from "lucide-react";

type ReviewExportDecisionProps = {
  readyToExport: boolean;
  issueCount: number;
  translationAttentionCount: number;
  questionCount: number;
  translatedCount: number;
  onReview: () => void;
  onExport: () => void;
};

export default function ReviewExportDecision({
  readyToExport,
  issueCount,
  translationAttentionCount,
  questionCount,
  translatedCount,
  onReview,
  onExport,
}: ReviewExportDecisionProps) {
  const totalAttentionCount = issueCount + translationAttentionCount;

  return (
    <div
      className={`mdk-review-export-hub ${
        readyToExport ? "is-ready" : "needs-review"
      }`}
      aria-live="polite"
    >
      <div className="mdk-review-export-hub__status">
        <span className="mdk-review-export-hub__status-icon">
          {readyToExport ? (
            <CheckCircle2 size={30} />
          ) : (
            <AlertTriangle size={30} />
          )}
        </span>
        <div>
          <span className="mdk-simple-eyebrow">المراجعة والتصدير</span>
          <h2>
            {readyToExport
              ? "الورقة جاهزة للمعاينة والتصدير"
              : "راجع الملاحظات ثم صدّر"}
          </h2>
          <p>
            {readyToExport
              ? "اختر المعاينة والتصدير، أو افتح الأسئلة لإجراء مراجعة أخيرة اختيارية."
              : `بقيت ${totalAttentionCount} ملاحظة تحتاج قرارك قبل إتاحة التصدير.`}
          </p>
        </div>
      </div>

      <div className="mdk-review-export-hub__actions" aria-label="إجراءات المراجعة والتصدير">
        <button
          type="button"
          className={
            readyToExport
              ? "mdk-simple-secondary-button"
              : "mdk-simple-primary-button is-large"
          }
          onClick={onReview}
        >
          <ListChecks size={19} />
          {readyToExport ? "مراجعة الأسئلة" : "مراجعة الملاحظات"}
        </button>
        <button
          type="button"
          className={
            readyToExport
              ? "mdk-simple-primary-button is-large"
              : "mdk-simple-secondary-button"
          }
          onClick={onExport}
          disabled={!readyToExport}
          aria-disabled={!readyToExport}
        >
          {readyToExport ? <Eye size={19} /> : <LockKeyhole size={18} />}
          {readyToExport ? "معاينة وتصدير" : "التصدير بعد المراجعة"}
        </button>
      </div>

      {!readyToExport ? (
        <div className="mdk-review-export-hub__issues" aria-label="ملخص الملاحظات">
          {issueCount > 0 ? (
            <div>
              <ListChecks size={18} />
              <span>ملاحظات الجاهزية</span>
              <strong>{issueCount}</strong>
            </div>
          ) : null}
          {translationAttentionCount > 0 ? (
            <div>
              <AlertTriangle size={18} />
              <span>ملاحظات الترجمة</span>
              <strong>{translationAttentionCount}</strong>
            </div>
          ) : null}
          <small>
            <LockKeyhole size={15} />
            التصدير متاح بعد إنهاء الملاحظات المطلوبة.
          </small>
        </div>
      ) : null}

      <details className="mdk-review-export-hub__summary">
        <summary>ملخص الورقة</summary>
        <div>
          <span>
            <strong>{questionCount}</strong>
            سؤالًا مستخرجًا
          </span>
          <span>
            <strong>{translatedCount}</strong>
            سؤالًا مترجمًا
          </span>
          <span>
            <Download size={17} />
            نسخة الطالب والمعلم من شاشة التصدير
          </span>
        </div>
      </details>
    </div>
  );
}
