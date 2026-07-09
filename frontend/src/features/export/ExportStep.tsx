import { Download, FileText } from 'lucide-react';
import type { GlossaryTerm, ProjectMetadata, QuestionItem } from '../../types/project';
import { MetricCard } from '../../components/MetricCard';

interface ExportStepProps {
  metadata: ProjectMetadata;
  questions: QuestionItem[];
  glossary: GlossaryTerm[];
}

export function ExportStep({ metadata, questions, glossary }: ExportStepProps) {
  const approvedQuestions = questions
    .filter((question) => question.status !== 'deleted')
    .sort((a, b) => a.orderIndex - b.orderIndex);
  const totalMarks = approvedQuestions.reduce((sum, question) => sum + (question.marks ?? 0), 0);
  const glossaryNeedsReview = glossary.filter((term) => term.status === 'needs_review').length;

  return (
    <div className="step-grid">
      <section className="form-card wide-card">
        <div className="section-heading">
          <p className="eyebrow">تصدير شكلي</p>
          <h3>جاهزية الورقة النهائية</h3>
          <p>هذه المرحلة لا تنشئ DOCX أو PDF فعليًا بعد. الهدف الآن تثبيت قرار التصدير والملخص النهائي.</p>
        </div>

        <div className="metrics-row">
          <MetricCard label="الأسئلة المصدّرة" value={approvedQuestions.length} hint="بعد الحذف" />
          <MetricCard label="مجموع الدرجات" value={totalMarks} hint="محسوب تلقائيًا" />
          <MetricCard label="مصطلحات تحتاج مراجعة" value={glossaryNeedsReview} hint="للمعلم فقط" />
        </div>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">بيانات الورقة</p>
          <h3>{metadata.paperTitle}</h3>
        </div>
        <dl className="metadata-list">
          <div><dt>المدرسة</dt><dd>{metadata.schoolName}</dd></div>
          <div><dt>المادة</dt><dd>{metadata.subject}</dd></div>
          <div><dt>الصف</dt><dd>{metadata.grade}</dd></div>
          <div><dt>الزمن</dt><dd>{metadata.duration}</dd></div>
          <div><dt>نوع النسخة</dt><dd>{metadata.outputMode === 'bilingual' ? 'ثنائية اللغة' : 'عربية نظيفة'}</dd></div>
          <div><dt>الصيغ</dt><dd>{metadata.exportFormats.join(' + ').toUpperCase()}</dd></div>
        </dl>
      </section>

      <section className="form-card">
        <div className="section-heading">
          <p className="eyebrow">أزرار مؤجلة</p>
          <h3>التصدير الفعلي في Phase 1-F</h3>
        </div>
        <button type="button" className="primary-button full-width" disabled>
          <Download size={18} />
          إنشاء الملفات لاحقًا
        </button>
        <div className="notice-card">
          <FileText size={22} />
          <span>DOCX وPDF مؤجلان عمدًا حتى لا نخلط الواجهة مع محرك التصدير قبل موعده.</span>
        </div>
      </section>
    </div>
  );
}
