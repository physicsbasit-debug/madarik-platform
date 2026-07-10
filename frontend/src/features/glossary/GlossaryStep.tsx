import { Sparkles } from 'lucide-react';
import type { GlossaryTerm } from '../../types/project';

interface GlossaryStepProps {
  glossary: GlossaryTerm[];
  onUpdateTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
  onGenerateGlossary: () => void;
}

export function GlossaryStep({ glossary, onUpdateTerm, onGenerateGlossary }: GlossaryStepProps) {
  return (
    <section className="form-card wide-card">
      <div className="section-heading split-heading">
        <div>
          <p className="eyebrow">قاموس الورقة</p>
          <h3>مصطلحات للمعلم فقط</h3>
          <p>القاموس لا يظهر للطالب في النسخة النهائية. دوره ضبط المصطلحات قبل مراجعة الأسئلة والترجمة لاحقًا.</p>
        </div>
        <button className="secondary-button" type="button" onClick={onGenerateGlossary}>
          <Sparkles size={18} />
          توليد قاموس من الأسئلة
        </button>
      </div>

      <div className="notice-card glossary-notice">
        <strong>Phase 1-E1:</strong>
        <span>استخراج المصطلحات هنا Rule-based من قائمة علوم أولية، وليس ترجمة AI. راجع المصطلحات قبل اعتمادها، فالتطبيق ليس مفتي المصطلحات بعد.</span>
      </div>

      <div className="glossary-table" role="table" aria-label="قاموس الورقة المستخرج">
        <div className="glossary-row header" role="row">
          <span>المصطلح الإنجليزي</span>
          <span>الترجمة العربية</span>
          <span>المادة</span>
          <span>الحالة</span>
        </div>

        {glossary.length === 0 ? (
          <div className="empty-state">لا توجد مصطلحات بعد. حوّل النص إلى أسئلة أولًا، ثم اضغط توليد قاموس من الأسئلة.</div>
        ) : null}

        {glossary.map((term) => (
          <div key={term.id} className="glossary-row" role="row">
            <strong dir="ltr">{term.englishTerm}</strong>
            <input
              value={term.arabicTerm}
              onChange={(event) => onUpdateTerm(term.id, { arabicTerm: event.target.value })}
              aria-label={`ترجمة ${term.englishTerm}`}
            />
            <span>{term.subject || 'غير محدد'}</span>
            <select
              value={term.status}
              onChange={(event) => onUpdateTerm(term.id, { status: event.target.value as GlossaryTerm['status'] })}
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
