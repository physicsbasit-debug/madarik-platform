import { CheckCheck, Loader2, Sparkles } from 'lucide-react';
import type { GlossaryTerm } from '../../types/project';

interface GlossaryStepProps {
  glossary: GlossaryTerm[];
  onUpdateTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
  onGenerateGlossary: () => void;
  onApproveAll: () => void;
  isBusy?: boolean;
}

export function GlossaryStep({
  glossary,
  onUpdateTerm,
  onGenerateGlossary,
  onApproveAll,
  isBusy = false,
}: GlossaryStepProps) {
  const completedNeedsReview = glossary.filter(
    (term) =>
      term.status === 'needs_review' &&
      term.englishTerm.trim().length > 0 &&
      term.arabicTerm.trim().length > 0,
  ).length;

  return (
    <section className="form-card wide-card">
      <div className="section-heading split-heading">
        <div>
          <p className="eyebrow">قاموس الورقة</p>
          <h3>مصطلحات للمعلم فقط</h3>
          <p>
            راجع المصطلحات التي عليها ملاحظة فقط، ثم اعتمد المصطلحات المكتملة
            دفعة واحدة.
          </p>
        </div>
        <div className="glossary-header-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={onGenerateGlossary}
            disabled={isBusy}
          >
            {isBusy ? (
              <Loader2 size={18} className="spin-icon" />
            ) : (
              <Sparkles size={18} />
            )}
            توليد القاموس
          </button>
          <button
            className="primary-button"
            type="button"
            onClick={onApproveAll}
            disabled={completedNeedsReview === 0 || isBusy}
          >
            <CheckCheck size={18} />
            اعتماد المكتمل ({completedNeedsReview})
          </button>
        </div>
      </div>

      <div className="notice-card glossary-notice">
        <strong>قاعدة الاعتماد الجماعي:</strong>
        <span>
          يعتمد النظام المصطلحات التي تحتوي ترجمة عربية مكتملة فقط، ويترك أي
          مصطلح ناقص للمراجعة بدل دفنه تحت زر جماعي متحمس أكثر من اللازم.
        </span>
      </div>

      <div className="glossary-table" role="table" aria-label="قاموس الورقة المستخرج">
        <div className="glossary-row header" role="row">
          <span>المصطلح الإنجليزي</span>
          <span>الترجمة العربية</span>
          <span>المادة</span>
          <span>الحالة</span>
        </div>

        {glossary.length === 0 ? (
          <div className="empty-state">
            لا توجد مصطلحات بعد. استخرج الأسئلة أولًا، ثم اضغط توليد القاموس.
          </div>
        ) : null}

        {glossary.map((term) => (
          <div key={term.id} className="glossary-row" role="row">
            <strong dir="ltr">{term.englishTerm}</strong>
            <input
              value={term.arabicTerm}
              onChange={(event) =>
                onUpdateTerm(term.id, { arabicTerm: event.target.value })
              }
              aria-label={`ترجمة ${term.englishTerm}`}
            />
            <span>{term.subject || 'غير محدد'}</span>
            <select
              value={term.status}
              onChange={(event) =>
                onUpdateTerm(term.id, {
                  status: event.target.value as GlossaryTerm['status'],
                })
              }
            >
              <option value="approved">معتمد</option>
              <option value="needs_review">يحتاج مراجعة</option>
            </select>
          </div>
        ))}
      </div>
    </section>
  );
}
