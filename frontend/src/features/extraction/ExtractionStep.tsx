import { ClipboardList, DatabaseZap, FileText, Image as ImageIcon, Wand2 } from 'lucide-react';
import type { ExtractedTextInfo, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExtractionStepProps {
  questions: QuestionItem[];
  extractedText: ExtractedTextInfo | null;
  onReloadDemo: () => void;
  onParseQuestions: () => void;
}

export function ExtractionStep({ questions, extractedText, onReloadDemo, onParseQuestions }: ExtractionStepProps) {
  const totalMarks = questions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const needsReview = questions.filter((question) => question.status === 'needs_review').length;
  const hasTextToParse = Boolean(extractedText?.isTextBased && extractedText.text.trim().length > 0);

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">Phase 1-I2: PDF نصي + OCR صور/PDF مصوّر مبدئي</p>
          <h3>النص الخام المستخرج</h3>
          <p>
            في هذه المرحلة نقرأ PDF النصي مباشرة، ونجرّب OCR إنجليزيًا مبدئيًا للصور وPDF المصوّر محدود الصفحات، ثم نحول النص إلى بطاقات أسئلة بقواعد أولية.
          </p>
        </div>

        <div className="metrics-row">
          <MetricCard label="بطاقات الأسئلة" value={questions.length} hint="من Backend أو بيانات تجريبية" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب من البطاقات" />
          <MetricCard label="تحتاج مراجعة" value={needsReview} hint="تقسيم آلي أولي" />
          <MetricCard label="أحرف النص" value={extractedText?.characterCount ?? 0} hint="من PDF أو OCR" />
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
          <div className="empty-state">ارفع PDF نصيًا أو صورة واضحة أو PDF مصوّرًا بسيطًا ليظهر هنا مقتطف النص المستخرج.</div>
        )}

        <div className="inline-actions">
          <button type="button" className="primary-button" onClick={onParseQuestions} disabled={!hasTextToParse}>
            <Wand2 size={18} />
            تحويل النص إلى بطاقات أسئلة
          </button>
          <button type="button" className="secondary-button" onClick={onReloadDemo}>
            <DatabaseZap size={18} />
            إعادة تحميل بيانات Backend التجريبية
          </button>
        </div>
      </section>

      <section className="question-preview-list wide-card">
        {questions.map((question, index) => (
          <article key={question.id} className="mini-question-card">
            <div>
              <span className="status-pill">السؤال {index + 1} | الأصلي {question.originalNumber}</span>
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
