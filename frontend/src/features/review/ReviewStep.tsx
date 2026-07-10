import { ArrowDown, ArrowUp, CheckCircle2, ImagePlus, Languages, RotateCcw, Trash2, X } from 'lucide-react';
import type { ChangeEvent } from 'react';
import type { QuestionItem, QuestionStatus, TranslationProviderStatus } from '../../types/project';

interface ReviewStepProps {
  questions: QuestionItem[];
  onUpdateQuestion: (questionId: string, updates: Partial<QuestionItem>) => void;
  onMoveQuestion: (questionId: string, direction: 'up' | 'down') => void;
  onTranslateQuestions: () => void;
  onBulkUpdateStatus: (status: QuestionStatus, includeDeleted?: boolean) => void;
  onUploadQuestionAsset: (questionId: string, file: File) => void;
  onDeleteQuestionAsset: (questionId: string, assetId: string) => void;
  translationProviderStatus: TranslationProviderStatus | null;
}

const statusLabels: Record<QuestionStatus, string> = {
  approved: 'معتمد',
  needs_review: 'يحتاج مراجعة',
  deleted: 'محذوف',
};

function formatFileSize(size: number) {
  if (size < 1024) return `${size} بايت`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} ك.ب`;
  return `${(size / (1024 * 1024)).toFixed(1)} م.ب`;
}

export function ReviewStep({
  questions,
  onUpdateQuestion,
  onMoveQuestion,
  onTranslateQuestions,
  onBulkUpdateStatus,
  onUploadQuestionAsset,
  onDeleteQuestionAsset,
  translationProviderStatus,
}: ReviewStepProps) {
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

  function handleAssetInput(questionId: string, event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    onUploadQuestionAsset(questionId, file);
  }

  return (
    <section className="review-layout">
      <div className="section-heading split-heading">
        <div>
          <p className="eyebrow">مراجعة الأسئلة</p>
          <h3>بطاقات مستقلة قابلة للتعديل والحذف والترتيب</h3>
          <p>أي سؤال محذوف لا يدخل في التصدير النهائي، ويُعاد ترقيم الأسئلة المعتمدة تلقائيًا. يمكن الآن ربط صورة أو جدول بكل سؤال يدويًا.</p>
        </div>
        <button className="primary-button" type="button" onClick={onTranslateQuestions} disabled={activeQuestions.length === 0}>
          <Languages size={18} />
          ترجمة الأسئلة
        </button>
      </div>

      <div className="notice-card translation-notice">
        <strong>مرفقات الأسئلة:</strong>
        <span>
          تستطيع ربط صور/جداول يدوية بالسؤال لتظهر في المراجعة والتصدير. استخراج الصور تلقائيًا من PDF مؤجل لمرحلة لاحقة.
        </span>
      </div>

      <div className="notice-card translation-notice">
        <strong>مزود الترجمة:</strong>
        <span>
          الوضع الحالي:
          {' '}
          {translationProviderStatus?.provider === 'mock' || !translationProviderStatus?.configured
            ? 'ترجمة تجريبية محلية مع fallback'
            : `مزود خارجي مفعل: ${translationProviderStatus.provider} / ${translationProviderStatus.model}`}
          . راجع الترجمة قبل أي تصدير، فالذكاء الاصطناعي ليس موظف ضبط جودة حتى الآن.
        </span>
      </div>

      <div className="review-bulk-actions">
        <button type="button" className="secondary-button compact" onClick={() => onBulkUpdateStatus('approved', false)} disabled={activeQuestions.length === 0}>
          <CheckCircle2 size={16} />
          اعتماد كل الأسئلة النشطة
        </button>
        <button type="button" className="secondary-button compact" onClick={() => onBulkUpdateStatus('needs_review', false)} disabled={activeQuestions.length === 0}>
          <RotateCcw size={16} />
          تحويل النشطة إلى تحتاج مراجعة
        </button>
        <button type="button" className="secondary-button compact" onClick={() => onBulkUpdateStatus('needs_review', true)} disabled={sortedQuestions.length === 0}>
          <RotateCcw size={16} />
          استعادة الكل للمراجعة
        </button>
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
                <option value="approved">{statusLabels.approved}</option>
                <option value="needs_review">{statusLabels.needs_review}</option>
                <option value="deleted">{statusLabels.deleted}</option>
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

            <section className="asset-panel">
              <div className="asset-panel-header">
                <div>
                  <strong>مرفقات السؤال</strong>
                  <span>{question.attachments.length > 0 ? `${question.attachments.length} مرفق` : 'لا توجد مرفقات بعد'}</span>
                </div>
                <label className="secondary-button compact asset-upload-button">
                  <ImagePlus size={16} />
                  إضافة صورة/جدول
                  <input type="file" accept="image/png,image/jpeg" onChange={(event) => handleAssetInput(question.id, event)} />
                </label>
              </div>

              {question.attachments.length > 0 ? (
                <div className="asset-gallery">
                  {question.attachments.map((asset) => (
                    <figure key={asset.id} className="asset-card">
                      <img src={`data:${asset.type};base64,${asset.dataBase64}`} alt={asset.name} />
                      <figcaption>
                        <span>{asset.name}</span>
                        <small>{formatFileSize(asset.size)}</small>
                      </figcaption>
                      <button type="button" className="asset-delete-button" onClick={() => onDeleteQuestionAsset(question.id, asset.id)} aria-label="حذف المرفق">
                        <X size={15} />
                      </button>
                    </figure>
                  ))}
                </div>
              ) : (
                <div className="attachment-box">{question.attachmentNote ?? 'يمكنك إضافة صورة رسم أو جدول لهذا السؤال يدويًا.'}</div>
              )}
            </section>

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
