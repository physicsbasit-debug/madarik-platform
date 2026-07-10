import { ArrowDown, ArrowUp, Languages, RotateCcw, Trash2 } from 'lucide-react';
import type { QuestionItem, QuestionStatus, TranslationProviderStatus } from '../../types/project';

interface ReviewStepProps {
  questions: QuestionItem[];
  onUpdateQuestion: (questionId: string, updates: Partial<QuestionItem>) => void;
  onMoveQuestion: (questionId: string, direction: 'up' | 'down') => void;
  onTranslateQuestions: () => void;
  translationProviderStatus: TranslationProviderStatus | null;
}

const statusLabels: Record<QuestionStatus, string> = {
  approved: 'معتمد',
  needs_review: 'يحتاج مراجعة',
  deleted: 'محذوف',
};

export function ReviewStep({ questions, onUpdateQuestion, onMoveQuestion, onTranslateQuestions, translationProviderStatus }: ReviewStepProps) {
  const sortedQuestions = [...questions].sort((a, b) => a.orderIndex - b.orderIndex);
  const activeQuestions = sortedQuestions.filter((question) => question.status !== 'deleted');

  function getCurrentNumber(questionId: string) {
    const index = activeQuestions.findIndex((question) => question.id === questionId);
    return index >= 0 ? index + 1 : '—';
  }

  function canMove(question: QuestionItem, direction: 'up' | 'down') {
    if (question.status === 'deleted') return false;
    const index = activeQuestions.findIndex((item) => item.id === question.id);
    if (direction === 'up') return index > 0;
    return index >= 0 && index < activeQuestions.length - 1;
  }

  return (
    <section className="review-layout">
      <div className="section-heading split-heading">
        <div>
          <p className="eyebrow">مراجعة الأسئلة</p>
          <h3>بطاقات مستقلة قابلة للتعديل والحذف والترتيب</h3>
          <p>أي سؤال محذوف لا يدخل في التصدير النهائي، ويُعاد ترقيم الأسئلة المعتمدة تلقائيًا.</p>
        </div>
        <button className="primary-button" type="button" onClick={onTranslateQuestions} disabled={activeQuestions.length === 0}>
          <Languages size={18} />
          ترجمة الأسئلة
        </button>
      </div>

      <div className="notice-card translation-notice">
        <strong>Phase 1-G1:</strong>
        <span>
          الترجمة تمر عبر طبقة مزود آمنة. الوضع الحالي:
          {' '}
          {translationProviderStatus?.provider === 'mock' || !translationProviderStatus?.configured
            ? 'ترجمة تجريبية محلية مع fallback'
            : `مزود خارجي مفعل: ${translationProviderStatus.provider} / ${translationProviderStatus.model}`}
          . راجع الترجمة قبل أي تصدير، فالذكاء الاصطناعي ليس موظف ضبط جودة حتى الآن.
        </span>
      </div>

      <div className="question-card-list">
        {sortedQuestions.map((question) => (
          <article key={question.id} className={`question-card ${question.status === 'deleted' ? 'is-deleted' : ''}`}>
            <header className="question-card-header">
              <div>
                <span className="status-pill">السؤال {getCurrentNumber(question.id)}</span>
                <strong>الأصل: {question.originalNumber}</strong>
              </div>
              <select
                value={question.status}
                onChange={(event) => onUpdateQuestion(question.id, { status: event.target.value as QuestionStatus })}
              >
                <option value="approved">معتمد</option>
                <option value="needs_review">يحتاج مراجعة</option>
                <option value="deleted">محذوف</option>
              </select>
            </header>

            <label>
              النص الأصلي
              <textarea value={question.originalText} readOnly dir="ltr" />
            </label>

            <label>
              الترجمة العربية
              <textarea
                value={question.translatedText}
                onChange={(event) => onUpdateQuestion(question.id, { translatedText: event.target.value })}
              />
            </label>

            <div className="question-tools-grid">
              <label>
                الدرجة
                <input
                  type="number"
                  min="0"
                  value={question.marks ?? ''}
                  onChange={(event) => {
                    const rawValue = event.target.value;
                    onUpdateQuestion(question.id, { marks: rawValue === '' ? null : Number(rawValue) });
                  }}
                />
              </label>

              <label>
                ملاحظة مراجعة
                <input
                  value={question.reviewNotes ?? ''}
                  onChange={(event) => onUpdateQuestion(question.id, { reviewNotes: event.target.value })}
                  placeholder="اختياري"
                />
              </label>
            </div>

            <div className="attachment-box">{question.attachmentNote}</div>

            <footer className="card-actions">
              <button type="button" className="secondary-button compact" disabled={!canMove(question, 'up')} onClick={() => onMoveQuestion(question.id, 'up')}>
                <ArrowUp size={16} />
                رفع
              </button>
              <button type="button" className="secondary-button compact" disabled={!canMove(question, 'down')} onClick={() => onMoveQuestion(question.id, 'down')}>
                <ArrowDown size={16} />
                إنزال
              </button>
              {question.status === 'deleted' ? (
                <button type="button" className="primary-button compact" onClick={() => onUpdateQuestion(question.id, { status: 'needs_review' })}>
                  <RotateCcw size={16} />
                  استعادة
                </button>
              ) : (
                <button type="button" className="danger-button compact" onClick={() => onUpdateQuestion(question.id, { status: 'deleted' })}>
                  <Trash2 size={16} />
                  حذف
                </button>
              )}
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}
