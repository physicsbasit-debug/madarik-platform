import { ClipboardList, DatabaseZap, FileText, Image as ImageIcon } from 'lucide-react';
import type { ExtractedTextInfo, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExtractionStepProps {
  questions: QuestionItem[];
  extractedText: ExtractedTextInfo | null;
  onReloadDemo: () => void;
}

export function ExtractionStep({ questions, extractedText, onReloadDemo }: ExtractionStepProps) {
  const totalMarks = questions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const needsReview = questions.filter((question) => question.status === 'needs_review').length;

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">Phase 1-C: استخراج PDF نصي</p>
          <h3>النص الخام المستخرج</h3>
          <p>
            في هذه المرحلة نقرأ النص القابل للتحديد من PDF فقط. تقسيم الأسئلة الحقيقي سيأتي في المرحلة التالية، فلا نخلط القارئ بالمحلل ونصنع حساء تقنيًا.
          </p>
        </div>

        <div className="metrics-row">
          <MetricCard label="عدد الأسئلة التجريبية" value={questions.length} hint="محفوظة مؤقتًا من Backend" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب من البطاقات" />
          <MetricCard label="تحتاج مراجعة" value={needsReview} hint="قبل التصدير" />
          <MetricCard label="أحرف PDF" value={extractedText?.characterCount ?? 0} hint="من PDF نصي" />
        </div>

        {extractedText ? (
          <div className={`extracted-text-panel ${extractedText.isTextBased ? 'success-panel' : 'warning-panel'}`}>
            <div className="panel-title">
              <FileText size={20} />
              <strong>{extractedText.message}</strong>
            </div>
            {extractedText.preview ? (
              <pre dir="ltr">{extractedText.preview}</pre>
            ) : (
              <p>لا يوجد نص قابل للعرض من الملف الحالي.</p>
            )}
          </div>
        ) : (
          <div className="empty-state">ارفع ملف PDF نصي من خطوة رفع الملف ليظهر هنا مقتطف النص المستخرج.</div>
        )}

        <button type="button" className="secondary-button" onClick={onReloadDemo}>
          <DatabaseZap size={18} />
          إعادة تحميل بيانات Backend التجريبية
        </button>
      </section>

      <section className="question-preview-list wide-card">
        {questions.map((question) => (
          <article key={question.id} className="mini-question-card">
            <div>
              <span className="status-pill">السؤال الأصلي {question.originalNumber}</span>
              <h4>{question.originalText}</h4>
              <p>{question.translatedText}</p>
            </div>
            <div className="mini-meta">
              <span>
                <ClipboardList size={16} />
                {question.marks ?? '—'} درجات
              </span>
              <span>
                <ImageIcon size={16} />
                {question.attachmentNote ?? 'لا يوجد مرفق'}
              </span>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
