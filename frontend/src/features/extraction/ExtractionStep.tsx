import { ClipboardList, Image as ImageIcon } from 'lucide-react';
import type { QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExtractionStepProps {
  questions: QuestionItem[];
}

export function ExtractionStep({ questions }: ExtractionStepProps) {
  const totalMarks = questions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const needsReview = questions.filter((question) => question.status === 'needs_review').length;

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">محاكاة استخراج الأسئلة</p>
          <h3>قائمة الأسئلة التجريبية</h3>
          <p>هذه البيانات ثابتة في Phase 1-A. في المراحل القادمة سيتم استخراجها من PDF أو الصور.</p>
        </div>

        <div className="metrics-row">
          <MetricCard label="عدد الأسئلة" value={questions.length} hint="بيانات تجريبية" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب من البطاقات" />
          <MetricCard label="تحتاج مراجعة" value={needsReview} hint="قبل التصدير" />
        </div>
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
