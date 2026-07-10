import { ClipboardList, DatabaseZap, Image as ImageIcon } from 'lucide-react';
import type { QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExtractionStepProps {
  questions: QuestionItem[];
  onReloadDemo: () => void;
}

export function ExtractionStep({ questions, onReloadDemo }: ExtractionStepProps) {
  const totalMarks = questions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const needsReview = questions.filter((question) => question.status === 'needs_review').length;

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">محاكاة استخراج الأسئلة من Backend</p>
          <h3>قائمة الأسئلة التجريبية</h3>
          <p>في Phase 1-B أصبحت الأسئلة والقاموس يأتيان من FastAPI كجلسة مؤقتة. استخراج PDF الحقيقي وOCR مؤجلان، فلا نخلط العجينة قبل ما تنضج.</p>
        </div>

        <div className="metrics-row">
          <MetricCard label="عدد الأسئلة" value={questions.length} hint="من Backend مؤقت" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب من البطاقات" />
          <MetricCard label="تحتاج مراجعة" value={needsReview} hint="قبل التصدير" />
        </div>

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
