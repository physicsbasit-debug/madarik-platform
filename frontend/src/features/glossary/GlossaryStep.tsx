import type { GlossaryTerm } from '../../types/project';

interface GlossaryStepProps {
  glossary: GlossaryTerm[];
  onUpdateTerm: (termId: string, updates: Partial<GlossaryTerm>) => void;
}

export function GlossaryStep({ glossary, onUpdateTerm }: GlossaryStepProps) {
  return (
    <section className="form-card wide-card">
      <div className="section-heading">
        <p className="eyebrow">قاموس الورقة</p>
        <h3>مصطلحات للمعلم فقط</h3>
        <p>القاموس لا يظهر للطالب في النسخة النهائية. دوره ضبط المصطلحات قبل مراجعة الأسئلة.</p>
      </div>

      <div className="glossary-table" role="table" aria-label="قاموس الورقة التجريبي">
        <div className="glossary-row header" role="row">
          <span>المصطلح الإنجليزي</span>
          <span>الترجمة العربية</span>
          <span>المادة</span>
          <span>الحالة</span>
        </div>

        {glossary.map((term) => (
          <div key={term.id} className="glossary-row" role="row">
            <strong dir="ltr">{term.englishTerm}</strong>
            <input
              value={term.arabicTerm}
              onChange={(event) => onUpdateTerm(term.id, { arabicTerm: event.target.value })}
              aria-label={`ترجمة ${term.englishTerm}`}
            />
            <span>{term.subject}</span>
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
